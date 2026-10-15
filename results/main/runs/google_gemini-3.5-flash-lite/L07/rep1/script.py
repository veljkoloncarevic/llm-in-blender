import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a container collection or just use the default scene collection
scene_collection = bpy.context.scene.collection

# 1. Rocket Body (Low-poly Cylinder: 8 vertices)
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=3.0,
    vertices=8,
    location=(0, 0, 1.5)
)
body_obj = bpy.context.active_object
body_obj.name = "RocketBody"

# 2. Rocket Nose Cone (Low-poly Cone: 8 vertices)
bpy.ops.mesh.primitive_cone_add(
    radius1=1.0,
    depth=1.5,
    vertices=8,
    location=(0, 0, 3.75)
)
nose_obj = bpy.context.active_object
nose_obj.name = "RocketNose"

# 3. Rocket Fins (3 fins, 120 degrees apart, made from scaled cubes)
fin_count = 3
fin_objects = []

for i in range(fin_count):
    angle = i * (2 * math.pi / fin_count)
    
    # Create a base cube for the fin
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(0, 0, 0)
    )
    fin_obj = bpy.context.active_object
    fin_obj.name = f"RocketFin_{i+1}"
    
    # Scale to make it a thin triangular-ish fin plate
    fin_obj.scale = (0.8, 0.15, 0.8)
    
    # Apply scale to keep transformations clean
    bpy.ops.object.transform_apply(scale=True)
    
    # Use BMesh to shape the cube into a swept fin profile
    mesh = fin_obj.data
    bm = bmesh.from_edit_mesh(mesh)
    
    # Move vertices to create a swept-back fin shape
    # The cube's local bounds are roughly -0.5 to 0.5
    for v in bm.verts:
        # Push top vertices outward/upward
        if v.co.z > 0:
            v.co.z += 0.4
            v.co.x += 0.3
            
    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Position the fin relative to the body radius
    # Body radius is 1.0, so place it slightly inside/at the edge
    fin_obj.location = (0, -0.9, 0.8)
    
    # Rotate around the Z axis to distribute evenly (120 degrees)
    fin_obj.rotation_euler = (0, 0, angle)
    
    fin_objects.append(fin_obj)

# Join all parts into a single low-poly rocket mesh to optimize face count and structure
objects_to_join = [body_obj, nose_obj] + fin_objects
bpy.ops.object.select_all(action='DESELECT')

for obj in objects_to_join:
    obj.select_set(True)

bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.join()

# Final Rocket Object
rocket = bpy.context.active_object
rocket.name = "LowPolyRocket"

# Center origin to geometry
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
rocket.location = (0, 0, 0)

# Optional: Set smooth/flat shading (low poly looks best with flat shading)
bpy.ops.object.shade_flat()
