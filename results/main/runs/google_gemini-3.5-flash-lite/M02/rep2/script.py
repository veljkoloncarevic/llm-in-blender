import bpy
import bmesh
from mathutils import noise

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create base grid mesh (subdivisions: 150x150 -> 22,500 vertices, ~44,000 faces)
# This fits comfortably within the 5,000 to 120,000 face count requirement.
subdiv = 150
size = 20.0

mesh = bpy.data.meshes.new(name="TerrainMesh")
obj = bpy.data.objects.new("Terrain", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=subdiv, y_segments=subdiv, size=size)

# 3. Apply procedural height using mathutils.noise.turbulence (Fractal Brownian Motion)
# This gives realistic multi-octave hilly terrain.
scale = 0.15
depth = 4
roughness = 0.5
height_multiplier = 3.5

for v in bm.verts:
    # Scale coordinates for noise sampling
    nx = v.co.x * scale
    ny = v.co.y * scale
    
    # turbulence returns a noise value, we offset z based on it
    n_val = noise.turbulence((nx, ny, 0.0), depth, fractal_type='FBM', roughness=roughness)
    v.co.z = n_val * height_multiplier

# Write back to mesh
bm.to_mesh(mesh)
bm.free()

# 4. Smooth shading and update normals
mesh.update()
for poly in mesh.polygons:
    poly.use_smooth = True

# 5. Set active object
bpy.view_layer.objects.active = obj
obj.select_set(True)
