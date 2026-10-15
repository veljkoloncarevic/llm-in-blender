import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a fence post (simple box)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
post = bpy.context.active_object
post.scale = (0.1, 0.1, 1.2)  # Thin tall post
bpy.ops.object.transform_apply(scale=True)

# Add Array modifier to duplicate posts
array_mod = post.modifiers.new(name="ArrayPosts", type='ARRAY')
array_mod.count = 8
array_mod.relative = True
array_mod.use_relative_offset = True
array_mod.relative_offset_displace = (1.2, 0, 0)  # Space posts 1.2 units apart

# Create first horizontal rail (lower)
bpy.ops.mesh.primitive_cube_add(size=1, location=(3.5, 0, 0.2))
rail_lower = bpy.context.active_object
rail_lower.scale = (4.5, 0.08, 0.1)  # Long thin rail
bpy.ops.object.transform_apply(scale=True)

# Create second horizontal rail (upper)
bpy.ops.mesh.primitive_cube_add(size=1, location=(3.5, 0, 0.9))
rail_upper = bpy.context.active_object
rail_upper.scale = (4.5, 0.08, 0.1)  # Long thin rail
bpy.ops.object.transform_apply(scale=True)

# Create a material for wooden appearance
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.55, 0.35, 0.2, 1.0)  # Brown wood color
bsdf.inputs["Roughness"].default_value = 0.7

# Assign material to all objects
for obj in [post, rail_lower, rail_upper]:
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# Select all objects
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = post

print("Fence scene created successfully with Array modifier on posts")
