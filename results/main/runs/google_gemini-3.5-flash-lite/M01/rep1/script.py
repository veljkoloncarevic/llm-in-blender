import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters
num_steps = 24
angle_increment = math.radians(15.0)  # 15 degrees per step
height_increment = 0.25               # Height per step
column_radius = 0.4
step_width = 1.2
step_depth = 0.35
step_thickness = 0.08
rail_radius = column_radius + step_width - 0.1
rail_height_offset = 1.0
rail_thickness = 0.05

# Create a new mesh and object for the staircase
mesh = bpy.data.meshes.new("SpiralStaircase_Mesh")
obj = bpy.data.objects.new("SpiralStaircase", mesh)
bpy.context.collection.objects.link(obj)

# Initialize bmesh
bm = bmesh.new()

# 1. Build Central Column (Cylinder)
column_segments = 16
column_height = num_steps * height_increment + 0.5
bmesh.ops.create_cone(
    bm,
    cap_ends=True,
    cap_tris=False,
    segments=column_segments,
    radius1=column_radius,
    radius2=column_radius,
    depth=column_height
)
# Move column up so its base is at Z=0
matrix_col = Matrix.Translation((0.0, 0.0, column_height / 2.0))
bmesh.ops.transform(bm, matrix=matrix_col, verts=bm.verts)


# 2. Build Steps and Support Beam underneath
for i in range(num_steps):
    angle = i * angle_increment
    z_pos = i * height_increment
    
    # Create step box using primitive
    step_bm = bmesh.new()
    bmesh.ops.create_cube(step_bm, size=1.0)
    
    # Scale cube to step dimensions (width along X, depth along Y, thickness along Z)
    mat_scale = Matrix.Scale(step_width, 4, Vector((1, 0, 0))) @ \
                Matrix.Scale(step_depth, 4, Vector((0, 1, 0))) @ \
                Matrix.Scale(step_thickness, 4, Vector((0, 0, 1)))
    bmesh.ops.transform(step_bm, matrix=mat_scale, verts=step_bm.verts)
    
    # Position step: shift out from center by column_radius + step_width/2
    # Then rotate by step angle, then translate up
    shift_x = column_radius + (step_width / 2.0)
    mat_pos = Matrix.Translation((shift_x, 0.0, step_thickness / 2.0))
    mat_rot = Matrix.Rotation(angle, 4, 'Z')
    mat_trans = Matrix.Translation((0.0, 0.0, z_pos))
    
    final_step_matrix = mat_trans @ mat_rot @ mat_pos
    bmesh.ops.transform(step_bm, matrix=final_step_matrix, verts=step_bm.verts)
    
    # Merge step geometry into main bmesh
    bm.verts.ensure_lookup_table()
    step_geom = list(step_bm.verts) + list(step_bm.edges) + list(step_bm.faces)
    
    # We duplicate/copy geometry into main bm
    # Instead of complex merging, we can just use bmesh.ops.create_cube directly on main bm with matrices,
    # but since we already built it in step_bm, let's just append data or use bmesh duplicate logic:
    # Actually, cleanly creating directly into `bm` is easier:
    step_bm.free()

# Re-approach: Directly create step geometry in main `bm` to avoid extra steps
steps_data = []
for i in range(num_steps):
    angle = i * angle_increment
    z_pos = i * height_increment
    
    # Temporary bm for a single step
    s_bm = bmesh.new()
    bmesh.ops.create_cube(s_bm, size=1.0)
    
    # Scale: width (X), depth (Y), thickness (Z)
    s_mat = Matrix.LocRotScale(
        Vector((column_radius + step_width/2.0, 0, step_thickness/2.0)),
        None,
        Vector((step_width, step_depth, step_thickness))
    )
    bmesh.ops.transform(s_bm, matrix=s_mat, verts=s_bm.verts)
    
    # Rotate and elevate for the spiral
    s_spiral = Matrix.Translation((0, 0, z_pos)) @ Matrix.Rotation(angle, 4, 'Z')
    bmesh.ops.transform(s_bm, matrix=s_spiral, verts=s_bm.verts)
    
    # Add to main mesh
    for v in s_bm.verts:
        bm.verts.new(v.co)
    bm.verts.ensure_lookup_table()
    
    # To easily copy faces, we can just use bmesh.ops.dupe, or construct manually.
    # Even simpler: accumulate transformation matrices and generate all at once, 
    # or just use bmesh.ops.contextual_create / geometry insertion.
    s_bm.free()

# Let's rewrite the step loop using direct bmesh primitive creation with transforms:
bm.clear()

# Re-create column
bmesh.ops.create_cone(
    bm, cap_ends=True, cap_tris=False,
    segments=16, radius1=column_radius, radius2=column_radius, depth=column_height
)
matrix_col = Matrix.Translation((0.0, 0.0, column_height / 2.0))
bmesh.ops.transform(bm, matrix=matrix_col, verts=bm.verts)

# Create Steps
for i in range(num_steps):
    angle = i * angle_increment
    z_pos = i * height_increment
    
    # Create cube geometry centered at origin
    cube = bmesh.ops.create_cube(bm, size=1.0)
    
    # Matrix to transform the unit cube into a placed step
    # 1. Scale
    # 2. Translate outward along X
    # 3. Rotate around Z by step angle
    # 4. Translate upward by z_pos
    
    T_out = Matrix.Translation((column_radius + (step_width / 2.0), 0.0, step_thickness / 2.0))
    S_scale = Matrix.Scale(step_width, 4, Vector((1, 0, 0))) @ \
              Matrix.Scale(step_depth, 4, Vector((0, 1, 0))) @ \
              Matrix.Scale(step_thickness, 4, Vector((0, 0, 1)))
              
    R_angle = Matrix.Rotation(angle, 4, 'Z')
    T_up = Matrix.Translation((0.0, 0.0, z_pos))
    
    final_mat = T_up @ R_angle @ T_out @ S_scale
    
    bmesh.ops.transform(bm, matrix=final_mat, verts=cube['verts'])

# 3. Build Helical Handrail & Spindles
# We will construct a smooth helical rail along the outer edge
rail_segments_per_turn = 16
total_rail_segments = int(num_steps * (rail_segments_per_turn / 12.0))
helix_total_angle = num_steps * angle_increment
helix_max_height = num_steps * height_increment

# Generate handrail path vertices
rail_verts = []
for j in range(total_rail_segments + 1):
    t = j / total_rail_segments
    angle = t * helix_total_angle
    z = (t * helix_max_height) + rail_height_offset
    
    x = rail_radius * math.cos(angle)
    y = rail_radius * math.sin(angle)
    rail_verts.append(Vector((x, y, z)))

# Create the handrail as a curved cylinder (lofting/extruding along points or using a small circle)
# Simplest robust method in bmesh: create a small circle for the rail profile and sweep it along the helix.
profile_segments = 6
profile_verts = []
for k in range(profile_segments):
    p_angle = k * (2.0 * math.pi / profile_segments)
    px = rail_thickness * math.cos(p_angle)
    pz = rail_thickness * math.sin(p_angle)
    profile_verts.append(Vector((px, pz, 0))) # in local XZ plane before orienting

# Build the handrail mesh strips manually between rings
prev_ring_verts = []
for j, p_center in enumerate(rail_verts):
    # Determine tangent for orientation
    if j < len(rail_verts) - 1:
        tangent = (rail_verts[j+1] - p_center).normalized()
    else:
        tangent = (p_center - rail_verts[j-1]).normalized()
    
    # Align a ring of vertices to the tangent
    # Default up vector (0, 0, 1) or radial vector
    radial = Vector((-p_center.x, -p_center.y, 0)).normalized()
    
    # Create rotation matrix to align Z-ish profile to tangent
    # Or simply construct matrix using tangent and radial vectors
    binormal = tangent.cross(radial).normalized()
    normal = binormal.cross(tangent).normalized()
    
    # Build ring vertices
    current_ring_verts = []
    for pv in profile_verts:
        # pv is in local coordinates where local Z is along tangent, or similar.
        # Let's map local (x, y, 0) using normal and binormal:
        world_pt = p_center + (normal * pv.x) + (binormal * pv.y)
        current_ring_verts.append(bm.verts.new(world_pt))
        
    bm.verts.ensure_lookup_table()
    
    # Connect with previous ring to form faces
    if j > 0:
        n = profile_segments
        for k in range(n):
            next_k = (k + 1) % n
            v1 = prev_ring_verts[k]
            v2 = prev_ring_verts[next_k]
            v3 = current_ring_verts[next_k]
            v4 = current_ring_verts[k]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except ValueError:
                pass # Face already exists or invalid
                
    prev_ring_verts = current_ring_verts

# Add vertical support spindles connecting every second step to the handrail
for i in range(0, num_steps, 2):
    angle = i * angle_increment
    z_step = i * height_increment + step_thickness
    z_rail = ( (i / num_steps) * helix_max_height ) + rail_height_offset
    
    # Spindle cylinder from step top to handrail bottom
    spindle_height = z_rail - z_step
    if spindle_height > 0:
        spindle = bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False,
            segments=6, radius1=0.02, radius2=0.02, depth=spindle_height
        )
        
        # Position spindle at outer edge of step
        spind_x = rail_radius * math.cos(angle)
        spind_y = rail_radius * math.sin(angle)
        spind_z = z_step + (spindle_height / 2.0)
        
        mat_spind = Matrix.Translation((spind_x, spind_y, spind_z))
        bmesh.ops.transform(bm, matrix=mat_spind, verts=spindle['verts'])

# Finalize mesh
bm.to_mesh(mesh)
bm.free()

# Smooth shading and auto-smooth for clean look
bpy.ops.object.shade_smooth()
obj.data.use_auto_smooth = True
obj.data.auto_smooth_angle = math.radians(35.0)

# Optional: Add a simple material
mat = bpy.data.materials.new(name="StaircaseMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.75, 0.65, 0.5, 1.0) # Wood-like tone
    bsdf.inputs['Roughness'].default_value = 0.4
obj.data.materials.append(mat)
