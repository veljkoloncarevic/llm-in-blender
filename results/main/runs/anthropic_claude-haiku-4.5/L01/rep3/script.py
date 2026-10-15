import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create tabletop
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
tabletop = bpy.context.active_object
tabletop.scale = (2, 1.5, 0.1)
bpy.ops.object.transform_apply(scale=True)

# Add Bevel modifier to tabletop
bevel_mod = tabletop.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.05
bevel_mod.segments = 2

# Create legs
leg_positions = [
    (-1.8, -1.3, -0.4),
    (1.8, -1.3, -0.4),
    (-1.8, 1.3, -0.4),
    (1.8, 1.3, -0.4)
]

for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.active_object
    leg.scale = (0.1, 0.1, 0.4)
    bpy.ops.object.transform_apply(scale=True)
    leg.name = f"Leg_{i+1}"

# Join all objects into one
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = tabletop
bpy.ops.object.join()

# Final object
final_obj = bpy.context.active_object
final_obj.name = "Table"
