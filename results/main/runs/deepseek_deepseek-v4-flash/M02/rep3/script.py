import bpy
import bmesh
import mathutils
from mathutils import noise

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Terrain parameters
segments_x = 100
segments_y = 100
size = 10.0
height_scale = 2.0

# Create base grid
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=segments_x, y_segments=segments_y, size=size)

# Fractal noise helper
def fbm(x, y):
    vec = mathutils.Vector((x, y, 0.0))
    value = 0.0
    amplitude = 1.0
    frequency = 0.1
    normalization = 0.0

    for _ in range(4):
        value += amplitude * noise.noise(vec * frequency)
        normalization += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return value / normalization

# Displace vertices according to noise
for v in bm.verts:
    v.co.z = fbm(v.co.x, v.co.y) * height_scale

# Create mesh and object
mesh = bpy.data.meshes.new("HillyTerrain")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("HillyTerrain", mesh)
bpy.context.collection.objects.link(obj)
