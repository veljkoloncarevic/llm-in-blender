import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Rocket body
bpy.ops.mesh.primitive_cylinder_add(
    vertices=12,
    radius=0.65,
    depth=3.0,
    end_fill_type='NGON',
    location=(0.0, 0.0, 0.0)
)
body = bpy.context.object
body.name = "Rocket_Body"

# Cone nose
bpy.ops.mesh.primitive_cone_add(
    vertices=12,
    radius1=0.65,
    radius2=0.0,
    depth=1.2,
    end_fill_type='NGON',
    location=(0.0, 0.0, 2.1)
)
nose = bpy.context.object
nose.name = "Rocket_Nose"

# Three evenly spaced fins
fin_radius = 0.78
fin_z = -0.95

for i in range(3):
    angle = math.radians(i * 120.0)
    x = fin_radius * math.cos(angle)
    y = fin_radius * math.sin(angle)

    bpy.ops.mesh.primitive_cube_add(
        location=(x, y, fin_z),
        rotation=(0.0, 0.0, angle)
    )
    fin = bpy.context.object
    fin.name = f"Rocket_Fin_{i + 1}"

    # Local X extends radially, local Y is tangential, and Z is vertical
    fin.scale = (0.42, 0.12, 0.58)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
