import bpy
import bmesh
import math

# -----------------------------------------------------------------------------
# Clean up existing scene
# -----------------------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# -----------------------------------------------------------------------------
# 1. House Walls (Cube)
# -----------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
walls = bpy.context.active_object
walls.name = "House_Walls"

# -----------------------------------------------------------------------------
# 2. Roof (Four-sided pyramid / Cone with 4 vertices)
# -----------------------------------------------------------------------------
bpy.ops.mesh.primitive_cone_add(
    vertices=4,
    radius1=1.4,
    depth=1.0,
    location=(0, 0, 2.5),
    rotation=(0, 0, math.radians(45))
)
roof = bpy.context.active_object
roof.name = "House_Roof"

# -----------------------------------------------------------------------------
# 3. Door (Cube, inset/flattened)
# -----------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.02, 0.5))
door = bpy.context.active_object
door.name = "House_Door"

# Scale door to look like a flat panel
door.scale = (0.3, 0.05, 0.5)
bpy.ops.object.transform_apply(scale=True)

# -----------------------------------------------------------------------------
# 4. Window (Base mesh for Mirror Modifier)
# -----------------------------------------------------------------------------
# Place one window on the left side (negative X), slightly protruding from the wall
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.6, -1.02, 1.2))
window = bpy.context.active_object
window.name = "House_Window"

# Scale window to a flat rectangular shape
window.scale = (0.25, 0.05, 0.35)
bpy.ops.object.transform_apply(scale=True)

# -----------------------------------------------------------------------------
# 5. Mirror Modifier for Windows
# -----------------------------------------------------------------------------
# Create an empty object to act as the mirror center (at the world origin, down Y axis)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
mirror_center = bpy.context.active_object
mirror_center.name = "MirrorCenter"

# Select the window and add a Mirror modifier referencing the empty
bpy.context.view_layer.objects.active = window
window.select_set(True)

mirror_mod = window.modifiers.new(name="WindowMirror", type='MIRROR')
mirror_mod.mirror_object = mirror_center
mirror_mod.use_axis[0] = True   # Mirror across X axis
mirror_mod.use_axis[1] = False  # Y axis off

# -----------------------------------------------------------------------------
# Materials (Simple flat low-poly colors)
# -----------------------------------------------------------------------------
def assign_material(obj, color):
    mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
    obj.data.materials.append(mat)

assign_material(walls, (0.9, 0.85, 0.75, 1.0))   # Cream walls
assign_material(roof, (0.7, 0.2, 0.1, 1.0))      # Terracotta roof
assign_material(door, (0.35, 0.2, 0.1, 1.0))     # Wooden door
assign_material(window, (0.1, 0.4, 0.6, 1.0))    # Glass blue

# Final selection setup
bpy.ops.object.select_all(action='DESELECT')
walls.select_set(True)
bpy.context.view_layer.objects.active = walls
