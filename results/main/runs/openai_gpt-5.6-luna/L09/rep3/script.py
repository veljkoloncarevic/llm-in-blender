import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused data blocks created by the prior scene
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)

# Materials
wood = bpy.data.materials.new("Warm Wooden Material")
wood.diffuse_color = (0.34, 0.12, 0.035, 1.0)
wood.use_nodes = True
wood_bsdf = wood.node_tree.nodes.get("Principled BSDF")
wood_bsdf.inputs["Base Color"].default_value = (0.34, 0.12, 0.035, 1.0)
wood_bsdf.inputs["Roughness"].default_value = 0.78

rail_wood = bpy.data.materials.new("Rail Wood Material")
rail_wood.diffuse_color = (0.48, 0.21, 0.065, 1.0)
rail_wood.use_nodes = True
rail_bsdf = rail_wood.node_tree.nodes.get("Principled BSDF")
rail_bsdf.inputs["Base Color"].default_value = (0.48, 0.21, 0.065, 1.0)
rail_bsdf.inputs["Roughness"].default_value = 0.82

# Dimensions
post_height = 3.4
post_width = 0.34
post_depth = 0.34
post_spacing = 2.0
first_post_x = -7.0

# Create the source post
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(first_post_x, 0.0, post_height / 2.0)
)
post = bpy.context.object
post.name = "Fence_Post_Array_8"
post.dimensions = (post_width, post_depth, post_height)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
post.data.materials.append(wood)

# Array modifier creates the remaining seven posts
array = post.modifiers.new("Eight Posts Array", 'ARRAY')
array.count = 8
array.use_relative_offset = False
array.use_constant_offset = True
array.constant_offset_displace = (post_spacing, 0.0, 0.0)

# Subtle edge softening
post_bevel = post.modifiers.new("Soft Wooden Edges", 'BEVEL')
post_bevel.width = 0.045
post_bevel.segments = 2
post_bevel.limit_method = 'ANGLE'

# Create the two horizontal rails
rail_length = (7.0 - first_post_x) - 0.18
rail_z_positions = (1.05, 2.25)

for index, z_position in enumerate(rail_z_positions, start=1):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0.0, 0.0, z_position)
    )
    rail = bpy.context.object
    rail.name = f"Horizontal_Rail_{index}"
    rail.dimensions = (rail_length, 0.22, 0.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    rail.data.materials.append(rail_wood)

    bevel = rail.modifiers.new("Soft Rail Edges", 'BEVEL')
    bevel.width = 0.035
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'

# Organize objects into a dedicated collection
fence_collection = bpy.data.collections.new("Wooden Fence")
bpy.context.scene.collection.children.link(fence_collection)

for obj in list(bpy.context.scene.collection.objects):
    if obj.name.startswith(("Fence_Post_Array_8", "Horizontal_Rail_")):
        for collection in list(obj.users_collection):
            collection.objects.unlink(obj)
        fence_collection.objects.link(obj)

# Set a useful scene unit scale and selection
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.view_layer.objects.active = post
post.select_set(True)
