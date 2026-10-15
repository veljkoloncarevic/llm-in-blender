import bpy

def remove_all_objects():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def add_cube(name, location, dimensions, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(scale=True, location=False, rotation=False)

    if material is not None:
        obj.data.materials.append(material)
    return obj

remove_all_objects()

# Simple brown wood material
wood_mat = bpy.data.materials.new("Wood")
wood_mat.use_nodes = True
bsdf = wood_mat.node_tree.nodes.get("Principled BSDF")
if bsdf is not None:
    bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1.0)
else:
    wood_mat.diffuse_color = (0.4, 0.25, 0.1, 1.0)

# One post, duplicated by Array modifier
post = add_cube("Post", (0.0, 0.0, 0.75), (0.1, 0.1, 1.5), wood_mat)

arr = post.modifiers.new(name="Array", type='ARRAY')
arr.count = 8
arr.use_relative_offset = False
arr.use_constant_offset = True
arr.relative_offset_displace = (0.0, 0.0, 0.0)
arr.constant_offset_displace = (1.0, 0.0, 0.0)

# Two horizontal rails connecting the 8 posts
rail_length = 7.1
rail_depth = 0.15
rail_height = 0.1
center_x = 3.5

add_cube("Rail_Top", (center_x, 0.0, 1.2), (rail_length, rail_depth, rail_height), wood_mat)
add_cube("Rail_Bottom", (center_x, 0.0, 0.5), (rail_length, rail_depth, rail_height), wood_mat)
