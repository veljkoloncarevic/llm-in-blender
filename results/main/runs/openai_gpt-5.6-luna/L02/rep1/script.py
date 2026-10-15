import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused mesh and material data
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
for material in list(bpy.data.materials):
    if material.users == 0:
        bpy.data.materials.remove(material)

def make_material(name, color, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

def smooth_object(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

def add_uv_sphere(name, location, radius, material, segments=24, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=radius,
        location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    smooth_object(obj)
    return obj

snow_material = make_material("Snow", (0.92, 0.97, 1.0), 0.9)
black_material = make_material("Coal", (0.015, 0.015, 0.02), 0.7)
orange_material = make_material("Carrot", (1.0, 0.22, 0.015), 0.75)

# Snowman body: three stacked spheres
add_uv_sphere("Bottom Snowball", (0.0, 0.0, 1.05), 1.05, snow_material)
add_uv_sphere("Middle Snowball", (0.0, 0.0, 2.65), 0.78, snow_material)
add_uv_sphere("Head", (0.0, 0.0, 3.90), 0.58, snow_material)

# Eyes, positioned toward the front (-Y)
add_uv_sphere("Left Eye", (-0.21, -0.515, 4.06), 0.085, black_material, 16, 8)
add_uv_sphere("Right Eye", (0.21, -0.515, 4.06), 0.085, black_material, 16, 8)

# Carrot nose: cone axis rotated from Z to point toward -Y
bpy.ops.mesh.primitive_cone_add(
    vertices=24,
    radius1=0.18,
    radius2=0.0,
    depth=0.72,
    location=(0.0, -0.72, 3.89),
    rotation=(1.5708, 0.0, 0.0)
)
nose = bpy.context.object
nose.name = "Carrot Nose"
nose.data.materials.append(orange_material)
smooth_object(nose)
