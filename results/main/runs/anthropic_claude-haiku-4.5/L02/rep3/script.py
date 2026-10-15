import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add body (large sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.0))
body = bpy.context.active_object
body.name = "Body"

# Add middle (medium sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0, 0, 2.5))
middle = bpy.context.active_object
middle.name = "Middle"

# Add head (small sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 3.8))
head = bpy.context.active_object
head.name = "Head"

# Add carrot nose (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0, depth=0.4, location=(0.5, 0, 3.8))
nose = bpy.context.active_object
nose.name = "Nose"
nose.rotation_euler = (0, 1.5708, 0)  # Rotate 90 degrees around Y axis

# Add left eye (small sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(-0.15, 0.3, 4.0))
left_eye = bpy.context.active_object
left_eye.name = "LeftEye"

# Add right eye (small sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.15, 0.3, 4.0))
right_eye = bpy.context.active_object
right_eye.name = "RightEye"

# Reduce polygon count by modifying sphere subdivision
# Re-create spheres with lower subdivision for optimization
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add body (large sphere) with fewer subdivisions
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.0), segments=16, ring_count=8)
body = bpy.context.active_object
body.name = "Body"

# Add middle (medium sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.7, location=(0, 0, 2.5), segments=16, ring_count=8)
middle = bpy.context.active_object
middle.name = "Middle"

# Add head (small sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 3.8), segments=16, ring_count=8)
head = bpy.context.active_object
head.name = "Head"

# Add carrot nose (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0, depth=0.4, location=(0.5, 0, 3.8), vertices=8)
nose = bpy.context.active_object
nose.name = "Nose"
nose.rotation_euler = (0, 1.5708, 0)  # Rotate 90 degrees around Y axis

# Add left eye (small sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(-0.15, 0.3, 4.0), segments=8, ring_count=4)
left_eye = bpy.context.active_object
left_eye.name = "LeftEye"

# Add right eye (small sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.15, 0.3, 4.0), segments=8, ring_count=4)
right_eye = bpy.context.active_object
right_eye.name = "RightEye"

# Deselect all
bpy.ops.object.select_all(action='DESELECT')
