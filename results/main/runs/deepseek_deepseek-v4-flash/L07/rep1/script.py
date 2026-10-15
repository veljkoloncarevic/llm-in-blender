import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Low-poly rocket parameters
body_radius = 0.5
body_length = 2.0
nose_length = 1.0
fin_scale = (0.5, 0.08, 0.8)          # radial extent, thickness, axial length
fin_radius = 1.0                       # distance from center to fin origin

# Cylinder body (8-sided)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=body_radius,
    depth=body_length,
    location=(0.0, 0.0, 0.0),
)
body = bpy.context.active_object
body.name = "RocketBody"

# Cone nose (8-sided, base matches body radius)
bpy.ops.mesh.primitive_cone_add(
    vertices=8,
    radius1=body_radius,
    depth=nose_length,
    location=(0.0, 0.0, body_length / 2 + nose_length / 2),
)
nose = bpy.context.active_object
nose.name = "RocketNose"

# Three fins from scaled cubes, evenly spaced 120° apart
for i in range(3):
    angle = i * (2.0 * math.pi / 3.0)
    x = fin_radius * math.cos(angle)
    y = fin_radius * math.sin(angle)

    bpy.ops.mesh.primitive_cube_add(
        size=2.0,
        location=(x, y, 0.0),
        rotation=(0.0, 0.0, angle),
    )
    fin = bpy.context.active_object
    fin.name = f"Fin_{i + 1}"
    fin.scale = fin_scale

# All objects remain separate; total face count is well under 800
