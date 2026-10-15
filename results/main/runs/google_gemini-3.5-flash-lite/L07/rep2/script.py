import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a clean collection for our rocket parts
collection = bpy.context.collection

# -------------------------------------------------------------
# 1. Rocket Body (Cylinder)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=3.0,
    vertices=8,
    location=(0, 0, 1.5)
)
body_obj = bpy.context.active_object
body_obj.name = "RocketBody"

# -------------------------------------------------------------
# 2. Nose Cone (Cone)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cone_add(
    radius1=1.0,
    depth=1.5,
    vertices=8,
    location=(0, 0, 3.75)
)
nose_obj = bpy.context.active_object
nose_obj.name = "RocketNose"

# -------------------------------------------------------------
# 3. Fins (Scaled Cubes arranged 120 degrees apart)
# -------------------------------------------------------------
fin_count = 3
fin_objects = []

for i in range(fin_count):
    angle = i * (2 * math.pi / fin_count)
    
    # Add a base cube
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    fin_obj = bpy.context.active_object
    fin_obj.name = f"RocketFin_{i+1}"
    
    # Scale it to look like a fin (thin, tapered profile via mesh editing or transform)
    # Dimensions: X=0.1 (thickness), Y=1.2 (chord length), Z=1.0 (height)
    fin_obj.scale = (0.15, 1.2, 1.0)
    
    # Apply scale so modifiers/rotations work cleanly
    bpy.ops.object.transform_apply(scale=True)
    
    # BMesh pass to shape the fin into a swept low-poly triangle
    # We shift vertices to create a swept-back look
    me = fin_obj.data
    bm = bmesh.from_edit_mesh(me)
    
    # Move vertices to make it a swept fin profile
    for v in bm.verts:
        # If vertex is high and towards the back/front, taper it
        if v.co.z > 0:
            v.co.y += 0.4  # Sweep backward at the top
            v.co.z -= 0.2  # Slight adjustment
            
    bmesh.update_edit_mesh(me)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Position the fin protruding out from the body radius
    # Body radius is 1.0, place fin center slightly inside or at the surface
    fin_obj.location = (0.0, 0.95, 0.8)
    
    # Rotate around Z axis to distribute evenly (120 degrees)
    fin_obj.rotation_euler = (0, 0, angle)
    
    fin_objects.append(fin_obj)

# -------------------------------------------------------------
# Join all parts into a single low-poly rocket object
# -------------------------------------------------------------
# Select all created mesh objects
bpy.ops.object.select_all(action='DESELECT')
body_obj.select_set(True)
nose_obj.select_set(True)
for fin in fin_objects:
    fin.select_set(True)

bpy.context.view_layer.objects.active = body_obj
bpy.ops.object.join()

# Final unified rocket object
rocket = bpy.context.active_object
rocket.name = "LowPolyRocket"

# Optional: Set smooth/flat shading to low-poly style (flat shading)
bpy.ops.object.shade_flat()
