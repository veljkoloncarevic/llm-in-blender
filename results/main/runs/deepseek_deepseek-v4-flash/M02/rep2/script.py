import bpy
import bmesh
from mathutils import Vector
from mathutils import noise

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Clean up orphan meshes
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

# Terrain parameters
SUBDIV_X = 200
SUBDIV_Y = 200
SIZE = 60.0
HEIGHT_SCALE = 4.0

# Create a new mesh and object
mesh = bpy.data.meshes.new("HillyTerrain")
obj = bpy.data.objects.new("HillyTerrain", mesh)
bpy.context.scene.collection.objects.link(obj)

# Build a grid using bmesh
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=SUBDIV_X, y_segments=SUBDIV_Y, size=SIZE)

# Displace vertices with a mix of noise octaves for rolling hills and detail
for v in bm.verts:
    x = v.co.x
    y = v.co.y

    # Broad hills
    n1 = noise.snoise(Vector((x * 0.03, y * 0.03, 0.0)))

    # Medium-sized terrain features
    n2 = noise.snoise(Vector((x * 0.08 + 10.0, y * 0.08 - 20.0, 0.0)))

    # Finer details
    n3 = noise.snoise(Vector((x * 0.25 + 100.0, y * 0.25 - 50.0, 0.0)))

    v.co.z = n1 * HEIGHT_SCALE + n2 * HEIGHT_SCALE * 0.5 + n3 * HEIGHT_SCALE * 0.2

# Write the bmesh into the mesh
bm.to_mesh(mesh)
bm.free()

# Enable smooth shading for a natural terrain appearance
for poly in mesh.polygons:
    poly.use_smooth = True

mesh.update()
