import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create main house body (cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
house_body = bpy.context.active_object
house_body.name = "HouseBody"

# Scale cube to be taller
house_body.scale = (1, 1, 1.2)
bpy.context.view_layer.objects.active = house_body
bpy.ops.object.transform_apply(scale=True)

# Create pyramid roof (4-sided cone)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.5, depth=1, location=(0, 0, 2.4))
roof = bpy.context.active_object
roof.name = "Roof"

# Create door
bpy.ops.mesh.primitive_cube_add(size=0.8, location=(0, 1.01, 0.6))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.4, 0.1, 0.8)
bpy.context.view_layer.objects.active = door
bpy.ops.object.transform_apply(scale=True)

# Create window (will be mirrored)
bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0.6, 1.01, 1.5))
window = bpy.context.active_object
window.name = "Window"
window.scale = (0.5, 0.1, 0.5)
bpy.context.view_layer.objects.active = window
bpy.ops.object.transform_apply(scale=True)

# Add Mirror modifier to window for symmetry
bpy.context.view_layer.objects.active = window
mirror_mod = window.modifiers.new(name="Mirror", type='MIRROR')
mirror_mod.use_axis[0] = True  # Mirror on X axis

# Join door and windows into one object for easier management
bpy.context.view_layer.objects.active = door
bpy.ops.object.select_all(action='DESELECT')
door.select_set(True)
window.select_set(True)
bpy.context.view_layer.objects.active = door
bpy.ops.object.join()
door.name = "DoorAndWindows"

# Set object origins and ensure clean geometry
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)

# Verify face count by checking mesh data
total_faces = 0
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        mesh = obj.data
        total_faces += len(mesh.polygons)

print(f"Total faces in scene: {total_faces}")

# Position all objects appropriately
bpy.context.view_layer.objects.active = house_body
house_body.location = (0, 0, 0)
roof.location = (0, 0, 2.4)
