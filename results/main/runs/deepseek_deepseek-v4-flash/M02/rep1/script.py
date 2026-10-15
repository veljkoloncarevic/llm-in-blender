import bpy
import bmesh
import mathutils
from mathutils import noise

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Terrain grid parameters
nx = 128
ny = 128
size = 20.0
height_scale = 2.0
seed = 42
noise.seed_set(seed)

# Build mesh data with bmesh
bm = bmesh.new()
verts = []

# Generate grid vertices with noise-based heights
for j in range(ny + 1):
    y = (j / ny - 0.5) * size
    for i in range(nx + 1):
        x = (i / nx - 0.5) * size
        pos = mathutils.Vector((x, y, 0.0))

        # Combine two noise frequencies to create hilly terrain
        h = noise.noise(pos * 0.5) * height_scale + 0.5 * noise.noise(pos * 2.0) * height_scale * 0.5

        vert = bm.verts.new((x, y, h))
        verts.append(vert)

# Create quad faces
for j in range(ny):
    for i in range(nx):
        i1 = j * (nx + 1) + i
        i2 = i1 + 1
        i3 = i1 + (nx + 1) + 1
        i4 = i1 + (nx + 1)
        try:
            bm.faces.new((verts[i1], verts[i2], verts[i3], verts[i4]))
        except ValueError:
            pass

# Recalculate face normals for consistent shading
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Transfer to mesh
mesh = bpy.data.meshes.new("HillyTerrain")
bm.to_mesh(mesh)
bm.free()

# Create and link object
obj = bpy.data.objects.new("HillyTerrain", mesh)
bpy.context.collection.objects.link(obj)

# Optional: smooth shading looks better on terrain
for poly in mesh.polygons:
    poly.use_smooth = True
