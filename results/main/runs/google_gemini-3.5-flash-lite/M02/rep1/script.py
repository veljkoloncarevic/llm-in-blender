import bpy
import bmesh
from mathutils import noise

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a grid mesh with sufficient subdivisions
# 150 x 150 grid = 22,500 vertices, 44,100 faces (fits within 5k-120k face range)
grid_size = 150
bpy.ops.mesh.primitive_grid_subdivide(
    size=20.0,
    resolution=grid_size,
    calc_uv_args=True
)

obj = bpy.context.active_object
obj.name = "ProceduralHillyTerrain"

# Ensure object is in object mode and data is accessible
mesh = obj.data

# 3. Apply noise function to vertex heights
# Using mathutils.noise.heterogeneous_terrain for a natural, mountainous look
scale = 0.15
height_multiplier = 2.5

for v in mesh.vertices:
    # Get local coordinates
    x, y, z = v.co
    
    # Generate fractal noise based on position
    # mathutils.noise.heterogeneous_terrain(vector, h, octaves, offset)
    nx = x * scale
    ny = y * scale
    nz = z * scale
    
    # Combine standard turbulence/noise for rolling hills with some roughness
    noise_val = noise.turbulence((nx, ny, nz), octaves=4, hurst=0.5, lacunarity=2.0)
    
    # Set the Z coordinate
    v.co.z = noise_val * height_multiplier

# 4. Update mesh normals and geometry
mesh.update()

# 5. Add a smooth modifier to soften the terrain appearance
smooth_mod = obj.modifiers.new(name="TerrainSmooth", type='SMOOTH')
smooth_mod.factor = 0.5
smooth_mod.iterations = 2

# Apply the modifier so the geometry is baked
bpy.ops.object.modifier_apply(modifier=smooth_mod.name)

# 6. Recalculate normals for proper shading
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Set smooth shading for the mesh
for p in mesh.polygons:
    p.use_smooth = True
