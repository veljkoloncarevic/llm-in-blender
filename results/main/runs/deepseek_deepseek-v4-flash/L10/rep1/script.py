import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create walls (cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
walls = bpy.context.active_object
walls.name = "Walls"

# Create roof (pyramid) - cone with 4 vertices, delete bottom face
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=1.5, depth=1.5, location=(0, 0, 2.75))
roof = bpy.context.active_object
roof.name = "Roof"
# Enter edit mode to delete bottom face
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
# Select bottom face (the one with normal pointing down)
for face in roof.data.polygons:
    if face.normal.z < 0:
        face.select = True
        break
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode='OBJECT')

# Create door (thin box) on front face (Y+)
bpy.ops.mesh.primitive_cube_add(size=(0.8, 0.2, 1.8), location=(0, 1, 0.9))
door = bpy.context.active_object
door.name = "Door"

# Create window (plane) on left side (X-), then mirror to right side
bpy.ops.mesh.primitive_plane_add(size=0.6, location=(0, 0, 0))
window = bpy.context.active_object
window.name = "Window"
# Rotate plane to face -X (outward on left wall)
window.rotation_euler = (0, -math.pi/2, 0)
bpy.ops.object.transform_apply(rotation=True)
# Move to left wall
window.location = (-1, 0, 1.2)
# Set origin to world origin (for mirror)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')  # place cursor at world origin first
# Actually, set cursor to (0,0,0) and then set origin
bpy.context.scene.cursor.location = (0, 0, 0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
# Add Mirror modifier across X
mirror = window.modifiers.new(name="Mirror", type='MIRROR')
mirror.use_axis[0] = True  # X axis
mirror.use_axis[1] = False
mirror.use_axis[2] = False

# Optionally add a ground plane (not required, but keeps scene tidy)
# bpy.ops.mesh.primitive_plane_add(size=10, location=(0,0,0))

print("Scene created successfully.")
