import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a simple ceramic material
mug_mat = bpy.data.materials.new("Coffee Mug Ceramic")
mug_mat.diffuse_color = (0.18, 0.42, 0.75, 1.0)
mug_mat.roughness = 0.28

handle_mat = bpy.data.materials.new("Handle Ceramic")
handle_mat.diffuse_color = (0.14, 0.34, 0.62, 1.0)
handle_mat.roughness = 0.28

# Create an open-topped cylindrical cup mesh
segments = 40
radius = 1.0
height = 1.8
bottom_z = 0.0
top_z = height

verts = []
for z in (bottom_z, top_z):
    for i in range(segments):
        angle = 2.0 * 3.141592653589793 * i / segments
        verts.append((radius * __import__('math').cos(angle),
                      radius * __import__('math').sin(angle),
                      z))

faces = []

# Cylindrical side walls
for i in range(segments):
    j = (i + 1) % segments
    faces.append((i, j, segments + j, segments + i))

# Bottom face only; the top remains open
faces.append(tuple(reversed(range(segments))))

mesh = bpy.data.meshes.new("Open Cup Mesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

cup = bpy.data.objects.new("Coffee Mug", mesh)
bpy.context.collection.objects.link(cup)
cup.data.materials.append(mug_mat)

# Solidify the open cup wall and bottom
solidify = cup.modifiers.new("Ceramic Wall Thickness", 'SOLIDIFY')
solidify.thickness = 0.12
solidify.offset = -1.0
solidify.use_rim = True

# Slightly soften the ceramic edges
bevel = cup.modifiers.new("Soft Ceramic Edges", 'BEVEL')
bevel.width = 0.035
bevel.segments = 2
bevel.limit_method = 'ANGLE'

# Smooth shading
for polygon in cup.data.polygons:
    polygon.use_smooth = True

# Create the handle as a torus in the vertical XZ plane
bpy.ops.mesh.primitive_torus_add(
    major_segments=32,
    minor_segments=8,
    location=(0.98, 0.0, 0.92),
    rotation=(1.5707963267948966, 0.0, 0.0),
    major_radius=0.62,
    minor_radius=0.115
)
handle = bpy.context.object
handle.name = "Mug Handle"
handle.data.materials.append(handle_mat)

# Slightly flatten the handle toward the mug for a natural attachment
handle.scale.y = 0.82
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Bevel the torus subtly
handle_bevel = handle.modifiers.new("Handle Edge Softness", 'BEVEL')
handle_bevel.width = 0.018
handle_bevel.segments = 2

for polygon in handle.data.polygons:
    polygon.use_smooth = True

# Set the mug and handle as the active selection
bpy.ops.object.select_all(action='DESELECT')
cup.select_set(True)
handle.select_set(True)
bpy.context.view_layer.objects.active = cup
