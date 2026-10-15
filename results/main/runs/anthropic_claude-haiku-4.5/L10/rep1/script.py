import bpy
import bmesh
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the main cube for walls
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
walls = bpy.context.active_object
walls.name = "Walls"

# Create a pyramid roof (cone with 4 vertices)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=1.5, depth=1.5, location=(0, 0, 2.75))
roof = bpy.context.active_object
roof.name = "Roof"

# Create door (simple plane)
bpy.ops.mesh.primitive_plane_add(size=0.8, location=(0, -1.01, 0.5))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.4, 0.8, 1)

# Create a window (simple plane)
bpy.ops.mesh.primitive_plane_add(size=0.4, location=(0.7, -1.01, 1.5))
window = bpy.context.active_object
window.name = "Window"

# Apply mirror modifier to window for symmetry
mirror_mod = window.modifiers.new(name="Mirror", type='MIRROR')
mirror_mod.axis = {'X'}
mirror_mod.use_clip = True

# Apply mirror modifier to door for symmetry (optional - creates double doors)
door_mirror = door.modifiers.new(name="Mirror", type='MIRROR')
door_mirror.axis = {'X'}
door_mirror.use_clip = True

# Join all objects into one for cleaner scene
bpy.context.view_layer.objects.active = walls
walls.select_set(True)
roof.select_set(True)
door.select_set(True)
window.select_set(True)

bpy.ops.object.join()

# Select the final object and apply modifiers to keep face count low
final_object = bpy.context.active_object
final_object.name = "House"

# Apply modifiers
for mod in final_object.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)

# Center the object
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
