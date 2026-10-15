import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the main house body (cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
house_body = bpy.context.active_object
house_body.name = "HouseBody"

# Scale the cube to be more house-like (wider, shorter)
house_body.scale = (1.5, 1.5, 1.2)

# Create the pyramid roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=1.8, depth=1.2, location=(0, 0, 2.6))
roof = bpy.context.active_object
roof.name = "Roof"
roof.rotation_euler = (0, 0, 0.785)  # Rotate 45 degrees to align with house

# Create door (simple cube, scaled to door shape)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 1.5, 0.5))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.4, 0.1, 0.8)

# Create a window on the left side (will be mirrored to right)
bpy.ops.mesh.primitive_cube_add(size=0.5, location=(-0.6, 1.5, 1.5))
window_left = bpy.context.active_object
window_left.name = "WindowLeft"
window_left.scale = (0.35, 0.1, 0.35)

# Add Mirror modifier to the left window to create right window
mirror_mod = window_left.modifiers.new(name="Mirror", type='MIRROR')
mirror_mod.use_axis[0] = True  # Mirror on X axis
mirror_mod.use_clip = False

# Create another window on the front-left side
bpy.ops.mesh.primitive_cube_add(size=0.5, location=(-0.6, 1.5, 1.8))
window_front_left = bpy.context.active_object
window_front_left.name = "WindowFrontLeft"
window_front_left.scale = (0.35, 0.1, 0.35)

# Add Mirror modifier to front-left window
mirror_mod2 = window_front_left.modifiers.new(name="Mirror", type='MIRROR')
mirror_mod2.use_axis[0] = True  # Mirror on X axis
mirror_mod2.use_clip = False

# Select all objects and apply modifiers to ensure they're baked in
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        # Apply modifiers
        for mod in obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        obj.select_set(False)

# Verify face count
total_faces = 0
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        total_faces += len(obj.data.polygons)

print(f"Total faces in scene: {total_faces}")
