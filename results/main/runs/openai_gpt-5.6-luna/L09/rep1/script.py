import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    if datablocks != bpy.data.materials:
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

# Materials
wood = bpy.data.materials.new("Warm Wood")
wood.diffuse_color = (0.28, 0.10, 0.035, 1.0)
wood.roughness = 0.82

rail_wood = bpy.data.materials.new("Rail Wood")
rail_wood.diffuse_color = (0.40, 0.17, 0.055, 1.0)
rail_wood.roughness = 0.86

def make_beveled_cube(name, location, scale, material, bevel_width=0.035):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2.0, scale[1] / 2.0, scale[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    obj.data.materials.append(material)

    bevel = obj.modifiers.new("Small softened edges", 'BEVEL')
    bevel.width = bevel_width
    bevel.segments = 1
    bevel.limit_method = 'ANGLE'

    return obj

# One source post, duplicated to eight posts using an Array modifier
post_spacing = 1.2
post = make_beveled_cube(
    "FencePost_ArraySource",
    (-4.2, 0.0, 1.15),
    (0.24, 0.24, 2.3),
    wood,
    0.035
)

array = post.modifiers.new("Eight Fence Posts", 'ARRAY')
array.count = 8
array.use_relative_offset = False
array.use_constant_offset = True
array.constant_offset_displace = (post_spacing, 0.0, 0.0)

# Two horizontal rails spanning the posts
rail_length = post_spacing * 7.0 + 0.18

upper_rail = make_beveled_cube(
    "Upper Horizontal Rail",
    (0.0, 0.0, 1.65),
    (rail_length, 0.17, 0.18),
    rail_wood,
    0.025
)

lower_rail = make_beveled_cube(
    "Lower Horizontal Rail",
    (0.0, 0.0, 0.72),
    (rail_length, 0.17, 0.18),
    rail_wood,
    0.025
)

# Keep the source post active and selected
bpy.ops.object.select_all(action='DESELECT')
post.select_set(True)
bpy.context.view_layer.objects.active = post
