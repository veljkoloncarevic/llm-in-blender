import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the three body spheres with lower subdivision
# Bottom sphere (largest)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.0,
    location=(0, 0, 1.0),
    segments=16,
    ring_count=8
)
bottom_sphere = bpy.context.active_object

# Middle sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.7,
    location=(0, 0, 2.5),
    segments=14,
    ring_count=7
)
middle_sphere = bpy.context.active_object

# Top sphere (head)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    location=(0, 0, 3.7),
    segments=12,
    ring_count=6
)
top_sphere = bpy.context.active_object

# Create carrot nose (cone)
bpy.ops.mesh.primitive_cone_add(
    radius1=0.15,
    radius2=0.0,
    depth=0.5,
    vertices=8,
    location=(0.5, 0, 3.7)
)
nose = bpy.context.active_object
# Rotate the cone to point outward
nose.rotation_euler = (0, 1.5708, 0)  # 90 degrees around Y axis

# Create left eye
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.1,
    location=(-0.15, 0.35, 3.9),
    segments=6,
    ring_count=3
)
left_eye = bpy.context.active_object

# Create right eye
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.1,
    location=(0.15, 0.35, 3.9),
    segments=6,
    ring_count=3
)
right_eye = bpy.context.active_object

# Verify face count
total_faces = 0
for obj in [bottom_sphere, middle_sphere, top_sphere, nose, left_eye, right_eye]:
    if obj.type == 'MESH':
        total_faces += len(obj.data.polygons)

print(f"Total faces in scene: {total_faces}")
