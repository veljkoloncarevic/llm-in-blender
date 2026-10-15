import bpy
import math

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Parameters
base_radius = 1.0
mid_radius = 0.7
head_radius = 0.5

base_z = 1.0
mid_z = base_z + base_radius + mid_radius - 0.15
head_z = mid_z + mid_radius + head_radius - 0.15

# Body: three stacked UV spheres (16 segments x 8 rings -> 128 faces each)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=base_radius,
    location=(0, 0, base_z)
)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=mid_radius,
    location=(0, 0, mid_z)
)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=head_radius,
    location=(0, 0, head_z)
)

# Eyes: two small spheres (8 segments x 4 rings -> 32 faces each)
eye_radius = 0.05
eye_x_offset = 0.18
eye_z_offset = 0.1
eye_y = math.sqrt(head_radius**2 - eye_x_offset**2 - eye_z_offset**2)

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8,
    ring_count=4,
    radius=eye_radius,
    location=(eye_x_offset, eye_y, head_z + eye_z_offset)
)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8,
    ring_count=4,
    radius=eye_radius,
    location=(-eye_x_offset, eye_y, head_z + eye_z_offset)
)

# Nose: cone pointing forward (+Y)
bpy.ops.mesh.primitive_cone_add(
    vertices=8,
    radius1=0.07,
    depth=0.4,
    location=(0, head_radius, head_z),
    rotation=(math.radians(-90), 0, 0),
    fill_type='NGON'
)
