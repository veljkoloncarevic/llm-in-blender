import bpy
import math

# Ensure clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
body_radius = 0.5
body_height = 2.0
nose_height = 1.5
fin_thickness = 0.05
fin_width = 0.4
fin_height = 1.0
fin_z_center = 1.0

# Cylinder body
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=body_radius,
    depth=body_height,
    location=(0, 0, body_height / 2)
)

# Cone nose
bpy.ops.mesh.primitive_cone_add(
    vertices=8,
    radius1=body_radius,
    radius2=0,
    depth=nose_height,
    location=(0, 0, body_height + nose_height / 2)
)

# Three fins, 120° apart
for i in range(3):
    angle = i * 2 * math.pi / 3

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    fin = bpy.context.object
    fin.scale = (fin_thickness, fin_width, fin_height)
    fin.rotation_euler = (0, 0, angle)

    dist = body_radius + fin_width / 2
    fin.location = (
        dist * (-math.sin(angle)),
        dist * math.cos(angle),
        fin_z_center
    )
