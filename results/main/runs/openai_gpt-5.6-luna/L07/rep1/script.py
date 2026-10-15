import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Rocket body
bpy.ops.mesh.primitive_cylinder_add(
    vertices=16,
    radius=0.7,
    depth=3.0,
    end_fill_type='NGON',
    location=(0.0, 0.0, 0.0)
)
body = bpy.context.object
body.name = "Rocket_Body"

# Cone nose
bpy.ops.mesh.primitive_cone_add(
    vertices=16,
    radius1=0.7,
    radius2=0.0,
    depth=1.4,
    end_fill_type='NGON',
    location=(0.0, 0.0, 2.2)
)
nose = bpy.context.object
nose.name = "Rocket_Nose"

# Three evenly spaced fins
fin_radius = 0.82
for i in range(3):
    angle = math.radians(i * 120.0)
    x = fin_radius * math.cos(angle)
    y = fin_radius * math.sin(angle)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x, y, -0.85),
        rotation=(0.0, 0.0, angle)
    )
    fin = bpy.context.object
    fin.name = f"Rocket_Fin_{i + 1}"
    fin.scale = (0.34, 0.11, 0.58)

# Use flat shading for the low-poly appearance
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for polygon in obj.data.polygons:
            polygon.use_smooth = False
