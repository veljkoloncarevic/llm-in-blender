import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Spring parameters
turns = 8
radius = 1.0
height = 4.0
wire_radius = 0.1
segments_per_turn = 64
circle_segments = 16

total_segments = turns * segments_per_turn
total_angle = 2.0 * math.pi * turns
pitch = height / total_angle  # vertical distance per radian

# Build coordinates for the helical tube
coords = []
for i in range(total_segments + 1):
    t = i / total_segments * total_angle
    cos_t = math.cos(t)
    sin_t = math.sin(t)

    pos = Vector((radius * cos_t, radius * sin_t, pitch * t - height / 2.0))

    # Frenet frame
    T = Vector((-radius * sin_t, radius * cos_t, pitch)).normalized()
    N = Vector((-cos_t, -sin_t, 0.0))  # points toward the helix axis
    B = T.cross(N)

    for k in range(circle_segments):
        phi = 2.0 * math.pi * k / circle_segments
        circle_vec = math.cos(phi) * N + math.sin(phi) * B
        coords.append(pos + wire_radius * circle_vec)

# Create mesh
mesh = bpy.data.meshes.new("CoilSpring")
bm = bmesh.new()
bm_verts = [bm.verts.new(v) for v in coords]

# Create quad faces between consecutive rings
for i in range(total_segments):
    base = i * circle_segments
    next_base = base + circle_segments
    for k in range(circle_segments):
        k_next = (k + 1) % circle_segments
        v1 = bm_verts[base + k]
        v2 = bm_verts[base + k_next]
        v3 = bm_verts[next_base + k_next]
        v4 = bm_verts[next_base + k]
        bm.faces.new((v1, v2, v3, v4))

bm.normal_update()
bm.to_mesh(mesh)
bm.free()

# Add object to scene
obj = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(obj)

# Smooth shading
for poly in mesh.polygons:
    poly.use_smooth = True
