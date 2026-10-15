import bpy
import bmesh
import math

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create the mug body as an open cylinder (open top, closed bottom)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.0,
    depth=1.5,
    location=(0.0, 0.0, 0.75),
    fill_type='NGON'
)
mug = bpy.context.active_object
mug.name = "Mug"

# Remove the top face so the cylinder is open at the top
mesh = mug.data
bm = bmesh.new()
bm.from_mesh(mesh)

for f in list(bm.faces):
    if all(v.co.z > 1.499 for v in f.verts):
        bm.faces.remove(f)

bm.to_mesh(mesh)
bm.free()

# Add a Solidify modifier to give the mug its wall thickness
solidify = mug.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.1
solidify.offset = -1  # thicken inward, keeping outer dimensions

# Create the handle as a torus, rotated to stand vertically on the side
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.55,
    minor_radius=0.12,
    major_segments=32,
    minor_segments=8,
    location=(1.05, 0.0, 0.75),
    rotation=(0.0, math.pi / 2.0, 0.0)
)
handle = bpy.context.active_object
handle.name = "Handle"

# The whole scene stays well below 3,000 faces
