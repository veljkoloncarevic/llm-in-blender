import bpy
import bmesh
import math
from mathutils import Matrix

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create rocket body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,
    depth=3,
    vertices=8,
    location=(0, 0, 0)
)
body = bpy.context.active_object
body.name = "RocketBody"

# Create nose cone
bpy.ops.mesh.primitive_cone_add(
    radius1=0.5,
    radius2=0,
    depth=1,
    vertices=8,
    location=(0, 0, 2)
)
nose = bpy.context.active_object
nose.name = "RocketNose"

# Create fins (scaled cubes)
fin_positions = [
    (0, 120),
    (120, 240),
    (240, 360)
]

for i, (start_angle, end_angle) in enumerate(fin_positions):
    # Create cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    fin = bpy.context.active_object
    fin.name = f"Fin{i+1}"
    
    # Scale the cube to make it fin-shaped
    # Scale down in Z (height), keep X, scale down Y (thickness)
    fin.scale = (0.3, 0.15, 0.8)
    
    # Move fin away from body center
    fin.location = (0.65, 0, -0.5)
    
    # Rotate around Z axis to position the fin
    angle_rad = math.radians(start_angle + (end_angle - start_angle) / 2)
    fin.rotation_euler = (0, 0, angle_rad)

# Select all objects and apply transforms
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Deselect all
bpy.ops.object.select_all(action='DESELECT')
