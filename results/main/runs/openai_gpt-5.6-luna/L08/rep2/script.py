import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create an open-topped mug body mesh
radius = 1.0
height = 1.8
segments = 48
bottom_z = 0.0
top_z = height

verts = []
for z in (bottom_z, top_z):
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        verts.append((radius * math.cos(angle), radius * math.sin(angle), z))

faces = []

# Outer cylindrical wall
for i in range(segments):
    j = (i + 1) % segments
    faces.append((i, j, segments + j, segments + i))

# Bottom face, oriented inward
faces.append(tuple(reversed(range(segments))))

mesh = bpy.data.meshes.new("MugBodyMesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

mug = bpy.data.objects.new("MugBody", mesh)
bpy.context.collection.objects.link(mug)

# Smooth shading
for poly in mesh.polygons:
    poly.use_smooth = True

# Hollow the mug with Solidify
solidify = mug.modifiers.new("Hollow Wall", 'SOLIDIFY')
solidify.thickness = 0.12
solidify.offset = -1.0
solidify.use_rim = True
solidify.material_offset = 0

# Slightly soften the edges while keeping the polygon count low
bevel = mug.modifiers.new("Soft Ceramic Edges", 'BEVEL')
bevel.width = 0.035
bevel.segments = 2
bevel.limit_method = 'ANGLE'

# Mug material
mug_material = bpy.data.materials.new("Ceramic")
mug_material.diffuse_color = (0.34, 0.10, 0.035, 1.0)
mug_material.roughness = 0.3
mug.data.materials.append(mug_material)

# Create a torus handle in a vertical XZ plane
bpy.ops.mesh.primitive_torus_add(
    major_segments=32,
    minor_segments=10,
    location=(1.02, 0.0, 0.9),
    major_radius=0.62,
    minor_radius=0.115,
    rotation=(math.pi / 2.0, 0.0, 0.0)
)
handle = bpy.context.object
handle.name = "MugHandle"

for poly in handle.data.polygons:
    poly.use_smooth = True

handle_bevel = handle.modifiers.new("Handle Edge Softening", 'BEVEL')
handle_bevel.width = 0.018
handle_bevel.segments = 2
handle_bevel.limit_method = 'ANGLE'

handle.data.materials.append(mug_material)

# Keep the mug centered neatly in the scene
mug.location.z = -height / 2.0
