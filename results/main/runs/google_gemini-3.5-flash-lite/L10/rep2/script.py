import bpy
import bmesh
from mathutils import Vector
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# -------------------------------------------------------------
# 1. House Walls (Cube)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
walls = bpy.context.active_object
walls.name = "House_Walls"

# -------------------------------------------------------------
# 2. Roof (Four-sided Pyramid / Cone with 4 vertices)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cone_add(
    vertices=4,
    radius1=1.45,
    depth=1.2,
    location=(0, 0, 2.6)
)
roof = bpy.context.active_object
roof.name = "House_Roof"
# Rotate 45 degrees to align roof edges with the cube walls
roof.rotation_euler.z = math.radians(45)

# -------------------------------------------------------------
# 3. Door
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.02, 0.5))
door = bpy.context.active_object
door.name = "House_Door"
door.scale = Vector((0.35, 0.05, 0.6))
bpy.context.view_layer.objects.active = door
bpy.ops.object.transform_apply(scale=True)

# -------------------------------------------------------------
# 4. Windows with Mirror Modifier
# -------------------------------------------------------------
# Place a single window on the left side (-X), then mirror across YZ plane for symmetry
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.02, 0.4, 1.2))
window = bpy.context.active_object
window.name = "House_Window"
window.scale = Vector((0.05, 0.3, 0.35))
bpy.context.view_layer.objects.active = window
bpy.ops.object.transform_apply(scale=True)

# Add Mirror Modifier to the window targeting the walls (which is centered at origin)
mirror_mod = window.modifiers.new(name="Mirror", type='MIRROR')
mirror_mod.use_axis[0] = True  # X axis mirror
mirror_mod.use_axis[1] = False
mirror_mod.use_axis[2] = False
mirror_mod.mirror_object = walls

# -------------------------------------------------------------
# 5. Materials (Low-poly flat colors using Principled BSDF)
# -------------------------------------------------------------
def assign_material(obj, color):
    mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.9
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

assign_material(walls, (0.85, 0.82, 0.75, 1.0))   # Off-white / beige walls
assign_material(roof, (0.7, 0.2, 0.15, 1.0))     # Terracotta red roof
assign_material(door, (0.35, 0.2, 0.1, 1.0))     # Wooden brown door
assign_material(window, (0.6, 0.8, 0.9, 1.0))    # Light blue glass

# Select walls as active object for clean final state
bpy.ops.object.select_all(action='DESELECT')
walls.select_set(True)
bpy.context.view_layer.objects.active = walls
