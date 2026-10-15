import bpy
import bmesh
from mathutils import noise

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a high-subdivision grid for terrain
# 150 x 150 vertices = 22,500 vertices, 22,201 quads (44,402 triangles)
# This comfortably fits the 5,000 - 120,000 face count requirement.
subdivisions = 150
size = 20.0

bpy.ops.mesh.primitive_grid_add(
    x_subdivisions=subdivisions,
    y_subdivisions=subdivisions,
    size=size,
    location=(0, 0, 0)
)

terrain_obj = bpy.context.active_object
terrain_obj.name = "ProceduralTerrain"

# 3. Apply noise function to vertex heights using BMesh
mesh = terrain_obj.data
bm = bmesh.from_edit_mesh(mesh) if terrain_obj.mode == 'EDIT' else bmesh.new()
if terrain_obj.mode != 'EDIT':
    bm.from_mesh(mesh)

# Ensure vertex coordinates can be modified
bm.verts.ensure_lookup_table()

# Multi-layered noise parameters for realistic hills
scale = 0.3
height_multiplier = 2.5

for v in bm.verts:
    # Get local coordinates
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # Layered noise (Fractal-like sum)
    # Base rolling hills
    n1 = noise.noise((x * scale, y * scale, 0.0)) * 1.0
    # Medium detail ridges
    n2 = noise.noise((x * scale * 2.5, y * scale * 2.5, 1.5)) * 0.4
    # Fine surface bump
    n3 = noise.noise((x * scale * 6.0, y * scale * 6.0, 3.0)) * 0.1
    
    # Combine noise layers
    combined_noise = n1 + n2 + n3
    
    # Optional: flatten out valleys slightly or shape the profile
    # Let's apply height scaling
    v.co.z = combined_noise * height_multiplier

# Update mesh from bmesh
bm.to_mesh(mesh)
bm.free()

# 4. Shade smooth for clean terrain appearance
for p in mesh.polygons:
    p.use_smooth = True

# 5. Add a Subdivision Surface modifier for extra organic smoothness (optional, keeps within poly limits)
subsurf = terrain_obj.modifiers.new(name="TerrainSubsurf", type='SUBSURF')
subsurf.levels = 1
subsurf.render_levels = 2
subsurf.uv_smooth_mode = 'PRESERVE_CORNERS'

# Set active object
bpy.context.view_layer.objects.active = terrain_obj
terrain_obj.select_set(True)
