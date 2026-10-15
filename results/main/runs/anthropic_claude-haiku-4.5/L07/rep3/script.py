import bpy
import bmesh
from mathutils import Matrix, Vector
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create rocket body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,
    depth=3,
    vertices=8,  # Low-poly: 8 vertices around
    location=(0, 0, 0)
)
body = bpy.context.active_object
body.name = "RocketBody"

# Create nose cone
bpy.ops.mesh.primitive_cone_add(
    radius1=0.5,
    radius2=0,
    depth=1,
    vertices=8,  # Low-poly: 8 vertices around
    location=(0, 0, 2)
)
nose = bpy.context.active_object
nose.name = "RocketNose"

# Create three fins from scaled cubes arranged 120 degrees apart
for i in range(3):
    angle = (i * 120) * math.pi / 180  # 120 degrees apart
    
    # Create a cube for the fin
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    fin = bpy.context.active_object
    fin.name = f"RocketFin{i}"
    
    # Scale the cube to make it fin-shaped: thin, tall, and narrow
    fin.scale = (0.15, 0.6, 0.3)  # thin in X, tall in Y, narrow in Z
    
    # Position fin away from body
    fin.location = (0.5 * math.cos(angle), 0.5 * math.sin(angle), -0.8)
    
    # Rotate fin to point outward and angle it
    fin.rotation_euler = (0, 0.3, angle)

# Join all objects into one mesh
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()

# Final object is now the combined rocket
rocket = bpy.context.active_object
rocket.name = "Rocket"

# Smooth shading for better appearance
bpy.context.view_layer.objects.active = rocket
bpy.ops.object.shade_smooth()

# Verify face count is under 800
mesh = rocket.data
face_count = len(mesh.polygons)
print(f"Total faces in rocket: {face_count}")
