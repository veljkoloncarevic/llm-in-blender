import bpy
import math

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Spring parameters
turns = 8
coil_radius = 1.0
height = 4.0
wire_radius = 0.12
longitudinal_segments = 256
radial_segments = 16

# Helix pitch per radian
pitch_per_radian = height / (turns * 2.0 * math.pi)
frame_scale = math.sqrt(1.0 + pitch_per_radian * pitch_per_radian)

vertices = []
faces = []

# Build swept circular tube along the helix
for i in range(longitudinal_segments + 1):
    t = (i / longitudinal_segments) * turns * 2.0 * math.pi
    ct = math.cos(t)
    st = math.sin(t)

    center = (
        coil_radius * ct,
        coil_radius * st,
        -height * 0.5 + pitch_per_radian * t
    )

    # Frenet frame for the helix
    normal = (-ct, -st, 0.0)
    tangent = (-st / frame_scale, ct / frame_scale, pitch_per_radian / frame_scale)
    binormal = (
        tangent[1] * normal[2] - tangent[2] * normal[1],
        tangent[2] * normal[0] - tangent[0] * normal[2],
        tangent[0] * normal[1] - tangent[1] * normal[0],
    )

    for j in range(radial_segments):
        a = (j / radial_segments) * 2.0 * math.pi
        ca = math.cos(a)
        sa = math.sin(a)

        vertices.append((
            center[0] + wire_radius * (normal[0] * ca + binormal[0] * sa),
            center[1] + wire_radius * (normal[1] * ca + binormal[1] * sa),
            center[2] + wire_radius * (normal[2] * ca + binormal[2] * sa),
        ))

# Connect tube rings
for i in range(longitudinal_segments):
    ring_a = i * radial_segments
    ring_b = (i + 1) * radial_segments

    for j in range(radial_segments):
        nj = (j + 1) % radial_segments
        faces.append((
            ring_a + j,
            ring_a + nj,
            ring_b + nj,
            ring_b + j,
        ))

# End caps
start_ring = list(range(radial_segments - 1, -1, -1))
end_base = longitudinal_segments * radial_segments
end_ring = [end_base + j for j in range(radial_segments)]

faces.append(tuple(start_ring))
faces.append(tuple(end_ring))

# Create mesh and object
mesh = bpy.data.meshes.new("CoilSpringMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

spring = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(spring)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True
