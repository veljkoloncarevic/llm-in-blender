import bpy
import bmesh
import math
from mathutils import Matrix

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Chain parameters
num_links = 12
major_radius = 1.0
minor_radius = 0.15
oval_aspect = 1.5
major_segments = 48
minor_segments = 16

# Distance between adjacent link centers along the chain axis (Z)
spacing = oval_aspect * major_radius

bm = bmesh.new()

for i in range(num_links):
    # Create a standard torus in the XY plane (hole along Z)
    result = bmesh.ops.create_torus(
        bm,
        major_segments=major_segments,
        minor_segments=minor_segments,
        mode='MAJOR_MINOR',
        major_radius=major_radius,
        minor_radius=minor_radius,
    )
    verts = result['verts']

    # Transform base torus:
    # 1. Scale along X to make the link oval.
    # 2. Rotate around Y so the oval lies in a plane containing the chain axis (Z).
    # 3. Rotate around Z by 90 degrees for alternating link orientation.
    # 4. Translate along Z to place the link in the chain.
    scale = Matrix.Scale(oval_aspect, 4, (1, 0, 0))
    rot_y = Matrix.Rotation(-math.pi / 2, 4, 'Y')
    rot_z = Matrix.Rotation(math.radians(90 * i), 4, 'Z')
    trans = Matrix.Translation((0.0, 0.0, i * spacing))

    mat = trans @ rot_z @ rot_y @ scale
    for v in verts:
        v.co = mat @ v.co

# Recalculate normals for the whole mesh
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Build the mesh object
mesh = bpy.data.meshes.new("ChainMesh")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("Chain", mesh)
bpy.context.collection.objects.link(obj)
