import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Bottom sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)

# Middle sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.7,
    location=(0.0, 0.0, 2.0)
)

# Top sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16,
    ring_count=8,
    radius=0.5,
    location=(0.0, 0.0, 2.7)
)

# Carrot nose (cone)
bpy.ops.mesh.primitive_cone_add(
    vertices=12,
    radius1=0.1,
    radius2=0.0,
    depth=0.5,
    location=(0.0, 0.5, 2.7),
    rotation=(math.pi / 2, 0.0, 0.0)
)

# Left eye
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8,
    ring_count=4,
    radius=0.08,
    location=(-0.1545, 0.464, 2.803)
)

# Right eye
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=8,
    ring_count=4,
    radius=0.08,
    location=(0.1545, 0.464, 2.803)
)
