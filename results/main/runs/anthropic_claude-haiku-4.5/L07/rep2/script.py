import bpy
import bmesh
from mathutils import Vector, Matrix
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create rocket body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,
    depth=3.0,
    vertices=8,
    location=(0, 0, 0)
)
body = bpy.context.active_object
body.name = "RocketBody"

# Create nose cone
bpy.ops.mesh.primitive_cone_add(
    radius1=0.5,
    radius2=0,
    depth=1.0,
    vertices=8,
    location=(0, 0, 2.0)
)
nose = bpy.context.active_object
nose.name = "NoseCone"

# Create fins as scaled cubes
fin_positions = [
    (0, 120, 0),
    (120, 120, 0),
    (240, 120, 0)
]

for i, rotation_z in enumerate(fin_positions):
    # Create a cube
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, 0, 0)
    )
    fin = bpy.context.active_object
    fin.name = f"Fin{i+1}"
    
    # Scale the cube to make it fin-shaped (thin, tall, wide)
    fin.scale = (0.3, 0.05, 0.6)
    
    # Position the fin away from the body center
    fin.location = (0.65, 0, 0.5)
    
    # Rotate around Z axis to distribute fins evenly (120 degrees apart)
    angle = math.radians(rotation_z)
    rotation_matrix = Matrix.Rotation(angle, 4, 'Z')
    fin.matrix_world = rotation_matrix @ Matrix.Translation(fin.location)
    fin.location = (fin.matrix_world @ Vector((0.65, 0, 0.5)))
    
    # Apply rotation
    fin.rotation_euler = (0, 0, angle)

# Join all objects into one
bpy.context.view_layer.objects.active = body
body.select_set(True)
nose.select_set(True)
for i in range(3):
    bpy.data.objects[f"Fin{i+1}"].select_set(True)

bpy.ops.object.join()

# Rename final object
bpy.context.active_object.name = "Rocket"

# Apply all transforms
bpy.ops.object.transform_apply(
    location=False,
    rotation=True,
    scale=True
)
