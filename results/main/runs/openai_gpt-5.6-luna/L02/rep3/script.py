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
black_mat = make_material("Coal", (0.015, 0.012, 0.01))
orange_mat = make_material("Carrot", (1.0, 0.22, 0.015))

def smooth_object(obj, material):
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj

def add_sphere(name, radius, location, material):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24,
        ring_count=12,
        radius=radius,
        location=location
    )
    obj = bpy.context.object
    obj.name = name
    return smooth_object(obj, material)

# Three stacked snow spheres
add_sphere("Bottom Snowball", 1.15, (0.0, 0.0, 1.15), snow_mat)
add_sphere("Middle Snowball", 0.88, (0.0, 0.0, 2.72), snow_mat)
add_sphere("Head", 0.66, (0.0, 0.0, 3.92), snow_mat)

# Carrot nose, pointing toward negative Y
bpy.ops.mesh.primitive_cone_add(
    vertices=20,
    radius1=0.22,
    radius2=0.0,
    depth=0.70,
    location=(0.0, -0.86, 3.92),
    rotation=(math.radians(90.0), 0.0, 0.0)
)
nose = bpy.context.object
nose.name = "Carrot Nose"
nose.data.materials.append(orange_mat)
for polygon in nose.data.polygons:
    polygon.use_smooth = True

# Coal eyes
add_sphere("Left Eye", 0.105, (-0.255, -0.585, 4.10), black_mat)
add_sphere("Right Eye", 0.105, (0.255, -0.585, 4.10), black_mat)
