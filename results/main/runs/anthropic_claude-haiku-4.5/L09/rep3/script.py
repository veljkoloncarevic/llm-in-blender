import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a wooden fence post
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
post = bpy.context.active_object
post.scale = (0.1, 0.1, 1.2)
post.name = "FencePost"

# Apply scale to make it permanent for the array modifier
bpy.context.view_layer.objects.active = post
bpy.ops.object.transform_apply(scale=True)

# Add Array modifier to duplicate the post
array_mod = post.modifiers.new(name="ArrayModifier", type='ARRAY')
array_mod.count = 8
array_mod.relative_scale_x = 3.0

# Create first horizontal rail (top)
bpy.ops.mesh.primitive_cube_add(size=1, location=(10.5, 0, 0.8))
rail_top = bpy.context.active_object
rail_top.scale = (10.5, 0.08, 0.1)
rail_top.name = "RailTop"
bpy.ops.object.transform_apply(scale=True)

# Create second horizontal rail (middle)
bpy.ops.mesh.primitive_cube_add(size=1, location=(10.5, 0, 0.2))
rail_bottom = bpy.context.active_object
rail_bottom.scale = (10.5, 0.08, 0.1)
rail_bottom.name = "RailBottom"
bpy.ops.object.transform_apply(scale=True)

# Create a simple wood material
mat = bpy.data.materials.new(name="WoodMaterial")
mat.diffuse_color = (0.6, 0.4, 0.2, 1.0)

# Assign material to all objects
for obj in [post, rail_top, rail_bottom]:
    obj.data.materials.append(mat)

# Set viewport shading to see the objects clearly
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

print("Wooden fence section created successfully!")
print(f"Total posts: 8 (via Array modifier on 1 post)")
print(f"Horizontal rails: 2")
