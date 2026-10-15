import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
    pass

# Materials
mug_mat = bpy.data.materials.new("Ceramic")
mug_mat.diffuse_color = (0.16, 0.055, 0.025, 1.0)
mug_mat.roughness = 0.28

handle_mat = mug_mat

# Mug body: open-top outer surface with a bottom face
segments = 48
radius = 1.5
height = 2.4
z_bottom = -height / 2
z_top = height / 2

verts = []
for z in (z_bottom, z_top):
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        verts.append((radius * math.cos(angle),
                      radius * math.sin(angle),
                      z))

faces = []

# Outer cylindrical wall
for i in range(segments):
    j = (i + 1) % segments
    faces.append((i, j, segments + j, segments + i))

# Bottom face, oriented downward
faces.append(tuple(reversed(range(segments))))

mesh = bpy.data.meshes.new("MugBodyMesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

mug = bpy.data.objects.new("CoffeeMug", mesh)
bpy.context.collection.objects.link(mug)
mug.data.materials.append(mug_mat)

# Smooth shading
for poly in mug.data.polygons:
    poly.use_smooth = True

# Create the hollow interior and wall thickness
solidify = mug.modifiers.new("Hollow ceramic wall", 'SOLIDIFY')
solidify.thickness = 0.14
solidify.offset = -1.0
solidify.use_rim = True

# Subtle edge softening
bevel = mug.modifiers.new("Rounded ceramic edges", 'BEVEL')
bevel.width = 0.035
bevel.segments = 2
bevel.limit_method = 'ANGLE'

# Handle: vertical torus intersecting the mug side
bpy.ops.mesh.primitive_torus_add(
    major_segments=32,
    minor_segments=10,
    mode='MAJOR_MINOR',
    major_radius=0.92,
    minor_radius=0.17,
    location=(1.43, 0.0, 0.0),
    rotation=(math.radians(90.0), 0.0, 0.0)
)

handle = bpy.context.object
handle.name = "MugHandle"
handle.data.materials.append(handle_mat)

for poly in handle.data.polygons:
    poly.use_smooth = True

handle_bevel = handle.modifiers.new("Handle edge softening", 'BEVEL')
handle_bevel.width = 0.018
handle_bevel.segments = 2
handle_bevel.limit_method = 'ANGLE'

# Keep the mug body selected and active
bpy.context.view_layer.objects.active = mug
mug.select_set(True)
handle.select_set(False)
