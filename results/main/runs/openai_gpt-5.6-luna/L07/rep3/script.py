import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rocket body
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.8,
    depth=3.0,
    location=(0.0, 0.0, 0.0)
)
body = bpy.context.object
body.name = "Rocket_Body"

# Nose cone
bpy.ops.mesh.primitive_cone_add(
    vertices=16,
    radius1=0.8,
    radius2=0.0,
    depth=1.4,
    location=(0.0, 0.0, 2.2)
)
nose = bpy.context.object
nose.name = "Rocket_Nose"

# Three evenly spaced fins
for i in range(3):
    angle = math.radians(i * 120.0)
    radial_distance = 0.8

    x = radial_distance * math.cos(angle)
    y = radial_distance * math.sin(angle)

    bpy.ops.mesh.primitive_cube_add(
        size=2.0,
        location=(x, y, -1.0)
    )
    fin = bpy.context.object
    fin.name = f"Rocket_Fin_{i + 1}"

    # Local Y axis points radially outward; local X is tangential
    fin.scale = (0.08, 0.325, 0.45)
    fin.rotation_euler[2] = angle - math.pi / 2.0

# Keep transforms as authored, with simple low-poly geometry
bpy.context.view_layer.objects.active = body
body.select_set(True)
