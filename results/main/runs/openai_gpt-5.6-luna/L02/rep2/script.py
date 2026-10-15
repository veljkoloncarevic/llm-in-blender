import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

snow_mat = make_material("Snow", (0.92, 0.97, 1.0))
orange_mat = make_material("Carrot Orange", (1.0, 0.25, 0.03))
black_mat = make_material("Coal Black", (0.01, 0.01, 0.01))

def smooth_object(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True

def add_uv_sphere(name, radius, location, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=12,
        radius=radius,
        location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    smooth_object(obj)
    return obj

# Snowman body: three stacked UV spheres
add_uv_sphere("Bottom Snowball", 2.0, (0.0, 0.0, 2.0), snow_mat)
add_uv_sphere("Middle Snowball", 1.5, (0.0, 0.0, 4.9), snow_mat)
add_uv_sphere("Head Snowball", 1.1, (0.0, 0.0, 7.2), snow_mat)

# Carrot nose, pointing toward the front (-Y)
bpy.ops.mesh.primitive_cone_add(
    vertices=24,
    radius1=0.32,
    radius2=0.0,
    depth=0.8,
    location=(0.0, -1.38, 7.15),
    rotation=(math.pi / 2.0, 0.0, 0.0)
)
nose = bpy.context.object
nose.name = "Carrot Nose"
nose.data.materials.append(orange_mat)
smooth_object(nose)

# Coal eyes
add_uv_sphere("Left Eye", 0.14, (-0.38, -1.02, 7.5), black_mat)
add_uv_sphere("Right Eye", 0.14, (0.38, -1.02, 7.5), black_mat)
