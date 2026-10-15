import bpy
import bmesh
from mathutils import Vector
import math

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# -------------------------------------------------------------------------
# 1. House Walls (Cube)
# -------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
walls = bpy.context.active_object
walls.name = "House_Walls"

# -------------------------------------------------------------------------
# 2. Roof (Four-sided pyramid / Cone with 4 vertices)
# -------------------------------------------------------------------------
bpy.ops.mesh.primitive_cone_add(
    vertices=4,
    radius1=1.45,
    depth=1.2,
    location=(0, 0, 2.6)
)
roof = bpy.context.active_object
roof.name = "House_Roof"
# Rotate 45 degrees to align corners with the walls
roof.rotation_euler = (0, 0, math.radians(45))

# -------------------------------------------------------------------------
# 3. Door (Simple thin box)
# -------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.02, 0.5))
door = bpy.context.active_object
door.name = "House_Door"
door.scale = (0.35, 0.08, 0.5)
bpy.ops.object.transform_apply(scale=True)

# -------------------------------------------------------------------------
# 4. Window with Mirror Modifier (Symmetrical placement)
# -------------------------------------------------------------------------
# Place a single window on the left side of the front (-Y face, X < 0)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, -1.02, 1.2))
window = bpy.context.active_object
window.name = "House_Window"
window.scale = (0.25, 0.08, 0.25)
bpy.ops.object.transform_apply(scale=True)

# Add Mirror modifier to the window so it mirrors across the YZ plane (X-axis symmetry)
mirror_mod = window.modifiers.new(name="SymmetryMirror", type='MIRROR')
mirror_mod.use_axis[0] = True   # X axis
mirror_mod.use_axis[1] = False  # Y axis
mirror_mod.use_axis[2] = False  # Z axis

# -------------------------------------------------------------------------
# 5. Materials (Basic Low-Poly Colors via Principled BSDF)
# -------------------------------------------------------------------------
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    return mat

mat_walls = create_material("Mat_Walls", (0.9, 0.88, 0.82, 1.0))   # Off-white
mat_roof = create_material("Mat_Roof", (0.75, 0.2, 0.15, 1.0))     # Terracotta red
mat_door = create_material("Mat_Door", (0.35, 0.2, 0.1, 1.0))      # Wood brown
mat_window = create_material("Mat_Window", (0.1, 0.2, 0.3, 1.0))   # Glass blue

walls.data.materials.append(mat_walls)
roof.data.materials.append(mat_roof)
door.data.materials.append(mat_door)
window.data.materials.append(mat_window)

# -------------------------------------------------------------------------
# 6. Final Scene Setup (Join structural elements for low-poly efficiency)
# -------------------------------------------------------------------------
# Select walls and roof and join them into a single low-poly house mesh
bpy.ops.object.select_all(action='DESELECT')
walls.select_set(True)
roof.select_set(True)
bpy.context.view_layer.objects.active = walls
bpy.ops.object.join()
walls.name = "House_Structure"

# Ensure smooth/flat shading appropriate for low-poly style
for obj in [walls, door, window]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_flat()

bpy.ops.object.select_all(action='DESELECT')
