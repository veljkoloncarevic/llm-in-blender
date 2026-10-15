import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

wall_mat = make_material("Walls", (0.65, 0.42, 0.22))
roof_mat = make_material("Roof", (0.18, 0.08, 0.04))
door_mat = make_material("Door", (0.12, 0.045, 0.02))
window_mat = make_material("Windows", (0.08, 0.35, 0.65))

# Create the main wall cube
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1.5))
walls = bpy.context.object
walls.name = "House_Walls"
walls.dimensions = (4.0, 4.0, 3.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
walls.data.materials.append(wall_mat)

# Create the four-sided pyramid roof
bpy.ops.mesh.primitive_cone_add(
    vertices=4,
    radius1=math.sqrt(8.0),
    radius2=0.0,
    depth=3.0,
    location=(0, 0, 4.5),
    rotation=(0, 0, math.radians(45))
)
roof = bpy.context.object
roof.name = "Four_Sided_Roof"
roof.data.materials.append(roof_mat)

# Create the front door
bpy.ops.mesh.primitive_cube_add(location=(0, -2.06, 1.1))
door = bpy.context.object
door.name = "Front_Door"
door.dimensions = (1.1, 0.12, 2.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
door.data.materials.append(door_mat)

# Create one front window, mirrored symmetrically across the house
bpy.ops.mesh.primitive_cube_add(location=(1.05, -2.06, 1.9))
window = bpy.context.object
window.name = "Front_Window_Mirrored"
window.dimensions = (0.75, 0.12, 0.8)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
window.data.materials.append(window_mat)

mirror = window.modifiers.new(name="Symmetric_Window", type='MIRROR')
mirror.use_axis[0] = True
mirror.use_axis[1] = False
mirror.use_axis[2] = False
mirror.mirror_object = walls

# Create a matching rear window pair using the same low-poly construction
bpy.ops.mesh.primitive_cube_add(location=(1.05, 2.06, 1.9))
rear_window = bpy.context.object
rear_window.name = "Rear_Window_Mirrored"
rear_window.dimensions = (0.75, 0.12, 0.8)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
rear_window.data.materials.append(window_mat)

rear_mirror = rear_window.modifiers.new(name="Symmetric_Rear_Window", type='MIRROR')
rear_mirror.use_axis[0] = True
rear_mirror.use_axis[1] = False
rear_mirror.use_axis[2] = False
rear_mirror.mirror_object = walls

# Keep the scene organized
for obj in bpy.context.scene.objects:
    obj.select_set(False)
walls.select_set(True)
bpy.context.view_layer.objects.active = walls
