import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Material
wood = bpy.data.materials.new("Warm Wood")
wood.diffuse_color = (0. thirty if False else 0.32, 0.12, 0.045, 1.0)
wood.roughness = 0.8

def make_cube(name, location, dimensions, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(wood)

    if bevel > 0:
        bevel_mod = obj.modifiers.new("Soft Wood Edges", 'BEVEL')
        bevel_mod.width = bevel
        bevel_mod.segments = 1
        bevel_mod.limit_method = 'ANGLE'

    return obj

# One source post, duplicated across the fence by an Array modifier
post = make_cube(
    "Fence Post",
    location=(0.0, 0.0, 1.25),
    dimensions=(0.24, 0.24, 2.5),
    bevel=0.045
)

array_mod = post.modifiers.new("Eight Fence Posts", 'ARRAY')
array_mod.count = 8
array_mod.use_relative_offset = False
array_mod.use_constant_offset = True
array_mod.constant_offset_displace = (1.35, 0.0, 0.0)

# Horizontal rails connecting the posts
rail_length = 1.35 * 7 + 0.24
make_cube(
    "Lower Horizontal Rail",
    location=(1.35 * 3.5, 0.0, 0.78),
    dimensions=(rail_length, 0.16, 0.18),
    bevel=0.035
)

make_cube(
    "Upper Horizontal Rail",
    location=(1.35 * 3.5, 0.0, 1.72),
    dimensions=(rail_length, 0.16, 0.18),
    bevel=0.035
)
