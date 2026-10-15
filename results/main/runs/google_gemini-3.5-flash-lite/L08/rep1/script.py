import bpy
import bmesh
from mathutils import Matrix, Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create the Mug Body (Cylinder)
# Keep segments moderate to stay well under 3,000 faces
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.2,
    vertices=32,
    location=(0, 0, 1.1)
)
mug = bpy.context.active_object
mug.name = "CoffeeMug"

# Ensure smooth shading
for f in mug.data.polygons:
    f.use_smooth = True

# Add Solidify modifier to make it hollow with thickness
solidify_mod = mug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify_mod.thickness = 0.12
solidify_mod.offset = -1.0 # inward thickness

# Add Subdivision Surface for a clean, organic look
subsurf_mod = mug.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf_mod.levels = 1
subsurf_mod.render_levels = 2

# 2. Create the Handle (Half Torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.12,
    major_segments=24,
    minor_segments=12,
    # Rotate to align vertically
    align='WORLD',
    location=(1.25, 0, 1.1),
    rotation=(0, 1.5708, 0)
)
handle = bpy.context.active_object
handle.name = "MugHandle"

# Edit handle: cut in half to make it a C-shape attached to the mug
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(handle.data)

# Delete the outer half of the torus (where x < local origin, or based on world coords)
# Since we rotated it, let's delete vertices based on world X coordinate being greater than 1.25
for v in bm.verts:
    # Transform vertex to world space
    co_world = handle.matrix_world @ v.co
    if co_world.x > 1.25 + 0.05: # Keep the side closer to the mug
        v.select = True
    else:
        v.select = False

# Delete selected geometry
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.select], context='VERTS')
bmesh.update_edit_mesh(handle.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Smooth shading for handle
for f in handle.data.polygons:
    f.use_smooth = True

# Add Subsurf to handle as well
handle_subsurf = handle.modifiers.new(name="Subsurf", type='SUBSURF')
handle_subsurf.levels = 1
handle_subsurf.render_levels = 2

# Select both and join them into a single mesh object
mug.select_set(True)
handle.select_set(True)
bpy.context.view_layer.objects.active = mug
bpy.ops.object.join()

# Final polish: auto smooth normals for crisp edges where needed
mug.data.use_auto_smooth = True
mug.data.auto_smooth_angle = 0.872665 # 50 degrees
