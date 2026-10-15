import bpy
import bmesh
from mathutils import Vector, Matrix
import math

# -----------------------------------------------------------------------------
# Clean up existing scene
# -----------------------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -----------------------------------------------------------------------------
# Parameters
# -----------------------------------------------------------------------------
die_size = 2.0
bevel_width = 0.12
pip_radius = 0.16
pip_depth = 0.04

# -----------------------------------------------------------------------------
# 1. Create the Base Die (Cube with Bevel)
# -----------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=die_size, location=(0, 0, 0))
die_obj = bpy.context.active_object
die_obj.name = "Die"

# Add Bevel modifier for rounded edges
bevel_mod = die_obj.modifiers.new(name="BevelEdges", type='BEVEL')
bevel_mod.width = bevel_width
bevel_mod.segments = 3
bevel_mod.profile = 0.5
bevel_mod.limit_method = 'NONE'

# -----------------------------------------------------------------------------
# 2. Define Pip Layouts (Face Centers & Offsets)
# -----------------------------------------------------------------------------
# Die faces configuration (Standard 6-sided die: opposite faces sum to 7)
# Face normals and their corresponding pip local positions relative to face center.
# We will construct a helper function to place pips on any face.

h = (die_size / 2.0) + 0.001  # Slightly outside/at the face boundary for boolean/merge

# Offsets for grid layouts (relative to face center)
d = 0.45  # distance from center
c = 0.0   # center

# Pip configurations per face number (1 to 6)
# Coordinates are in 2D (u, v) on the face plane
pip_layouts = {
    1: [(c, c)],
    2: [(-d, -d), (d, d)],
    3: [(-d, -d), (c, c), (d, d)],
    4: [(-d, -d), (-d, d), (d, -d), (d, d)],
    5: [(-d, -d), (-d, d), (c, c), (d, -d), (d, d)],
    6: [(-d, -d), (-d, c), (-d, d), (d, -d), (d, c), (d, d)]
}

# Face orientations: (Normal Vector, Up Vector for the 2D plane)
face_data = {
    1: (Vector((0, 0, 1)), Vector((0, 1, 0))),   # Top (+Z) -> 1
    6: (Vector((0, 0, -1)), Vector((0, 1, 0))),  # Bottom (-Z) -> 6
    2: (Vector((0, 1, 0)), Vector((0, 0, -1))),  # Front (+Y) -> 2
    5: (Vector((0, -1, 0)), Vector((0, 0, 1))),  # Back (-Y) -> 5
    3: (Vector((1, 0, 0)), Vector((0, 0, 1))),   # Right (+X) -> 3
    4: (Vector((-1, 0, 0)), Vector((0, 0, 1))),  # Left (-X) -> 4
}

# -----------------------------------------------------------------------------
# 3. Create Pips as Mesh Geometry and join to Die
# -----------------------------------------------------------------------------
# We'll use bmesh to build all pips in a single mesh, then join/boolean or 
# simply inset/extrude them, but shallow spheres/cylinders mapped to faces 
# look best. Let's construct a single bmesh for all pips.

bm_pips = bmesh.new()

for face_num, (normal, up_vec) in face_data.items():
    # Compute basis vectors for the face
    # normal is Z-axis of the face local space
    z_axis = normal.normalized()
    x_axis = up_vec.cross(z_axis).normalized()
    y_axis = z_axis.cross(x_axis).normalized()
    
    face_center = z_axis * (die_size / 2.0)
    
    for (u, v) in pip_layouts[face_num]:
        # Position of pip on face
        pip_center = face_center + (x_axis * u) + (y_axis * v)
        
        # Create a shallow cylinder / sphere cap for the pip
        # We'll make a small UV sphere or cylinder
        # To keep poly count extremely low, an 8-segment cylinder cap works great.
        seg = 8
        r = pip_radius
        depth = pip_depth
        
        # Build a small disc/cylinder pointing along 'normal'
        # Base center: pip_center
        # Tip center: pip_center - normal * depth (recessed)
        
        # Create vertices for a shallow cap
        verts = []
        # Center vertex at bottom of indent
        v_bottom = bm_pips.verts.new(pip_center - z_axis * depth)
        
        # Rim vertices
        rim_verts = []
        for i in range(seg):
            angle = 2.0 * math.pi * i / seg
            # Circle in local face coordinates
            cx = math.cos(angle) * r
            cy = math.sin(angle) * r
            v_pos = pip_center + (x_axis * cx) + (y_axis * cy)
            rim_verts.append(bm_pips.verts.new(v_pos))
            
        bm_pips.verts.ensure_lookup_table()
        
        # Make fan faces from bottom to rim
        for i in range(seg):
            next_i = (i + 1) % seg
            bm_pips.faces.new((v_bottom, rim_verts[i], rim_verts[next_i]))

# Create object from pips bmesh
pips_mesh = bpy.data.meshes.new("PipsMesh")
bm_pips.to_mesh(pips_mesh)
bm_pips.free()

pips_obj = bpy.data.objects.new("Pips", pips_mesh)
bpy.context.collection.objects.link(pips_obj)

# -----------------------------------------------------------------------------
# 4. Combine Die and Pips using Boolean Modifier (Difference)
# -----------------------------------------------------------------------------
bool_mod = die_obj.modifiers.new(name="PipBoolean", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = pips_obj
bool_mod.solver = 'FAST'

# Apply the modifiers to bake geometry and keep face count low & clean
bpy.context.view_layer.objects.active = die_obj
bpy.ops.object.modifier_apply(modifier="PipBoolean")
bpy.ops.object.modifier_apply(modifier="BevelEdges")

# Remove the temporary pips object
bpy.data.objects.remove(pips_obj, do_unlink=True)

# -----------------------------------------------------------------------------
# 5. Final Polish (Smooth Shading & Auto Smooth)
# -----------------------------------------------------------------------------
bpy.ops.object.shade_smooth()
die_obj.data.use_auto_smooth = True
die_obj.data.auto_smooth_angle = math.radians(35.0)

# Ensure correct orientation
bpy.ops.object.select_all(action='DESELECT')
die_obj.select_set(True)
bpy.context.view_layer.objects.active = die_obj
