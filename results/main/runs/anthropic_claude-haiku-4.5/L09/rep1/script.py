import bpy
import bmesh
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a single fence post
post_width = 0.1
post_height = 2.0
post_depth = 0.1

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
post = bpy.context.active_object
post.scale = (post_width, post_depth, post_height)
post.name = "FencePost"

# Apply scale to geometry
bpy.context.view_layer.objects.active = post
bpy.ops.object.transform_apply(scale=True)

# Add Array modifier to duplicate posts
array_mod = post.modifiers.new(name="ArrayPosts", type='ARRAY')
array_mod.count = 8
array_mod.relative = True
array_mod.use_relative_offset = True
array_mod.relative_offset_displace = (0.5, 0, 0)  # 0.5 units apart

# Create first horizontal rail (top)
rail_width = 4.0  # Spans across all posts
rail_height = 0.08
rail_depth = 0.08
rail_y_offset = 0.0
rail_z_top = 1.6

bpy.ops.mesh.primitive_cube_add(size=1, location=(1.75, rail_y_offset, rail_z_top))
rail_top = bpy.context.active_object
rail_top.scale = (rail_width, rail_depth, rail_height)
rail_top.name = "RailTop"

bpy.context.view_layer.objects.active = rail_top
bpy.ops.object.transform_apply(scale=True)

# Create second horizontal rail (bottom)
rail_z_bottom = 0.6

bpy.ops.mesh.primitive_cube_add(size=1, location=(1.75, rail_y_offset, rail_z_bottom))
rail_bottom = bpy.context.active_object
rail_bottom.scale = (rail_width, rail_depth, rail_height)
rail_bottom.name = "RailBottom"

bpy.context.view_layer.objects.active = rail_bottom
bpy.ops.object.transform_apply(scale=True)

# Apply wood-style material to all objects
wood_material = bpy.data.materials.new(name="WoodMaterial")
wood_material.use_nodes = True
bsdf = wood_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.6, 0.4, 0.2, 1.0)  # Wood color
bsdf.inputs[9].default_value = 0.3  # Roughness

for obj in [post, rail_top, rail_bottom]:
    if obj.data.materials:
        obj.data.materials[0] = wood_material
    else:
        obj.data.materials.append(wood_material)

# Ensure we're under 1000 faces
# Post: 12 faces * 8 posts = 96 faces
# Rail top: 12 faces
# Rail bottom: 12 faces
# Total: ~120 faces (well under 1000)

print("Fence scene created successfully!")
print(f"Post face count: {len(post.data.polygons)}")
print(f"Rail top face count: {len(rail_top.data.polygons)}")
print(f"Rail bottom face count: {len(rail_bottom.data.polygons)}")
