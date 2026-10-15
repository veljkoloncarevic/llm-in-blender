import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Spring parameters
turns = 8
centerline_radius = 1.0
height = 4.0
wire_radius = 0.12

# Mesh resolution
longitudinal_segments = 640
cross_section_segments = 16

total_angle = turns * 2.0 * math.pi
pitch_per_radian = height / total_angle

vertices = []
faces = []

# Generate swept circular tube along the helix
for i in range(longitudinal_segments + 1):
    u = i / longitudinal_segments
    theta = total_angle * u

    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    center = Vector((
        centerline_radius * cos_t,
        centerline_radius * sin_t,
        -height * 0.5 + height * u
    ))

    # Unit tangent of the helix
    tangent = Vector((
        -centerline_radius * sin_t,
        centerline_radius * cos_t,
        pitch_per_radian
    )).normalized()

    # Radial inward normal
    normal = Vector((-cos_t, -sin_t, 0.0)).normalized()

    # Orthogonal binormal
    binormal = tangent.cross(normal).normalized()

    for j in range(cross_section_segments):
        phi = 2.0 * math.pi * j / cross_section_segments
        offset = (
            wire_radius * math.cos(phi) * normal +
            wire_radius * math.sin(phi) * binormal
        )
        vertices.append(tuple(center + offset))

# Connect tube rings
for i in range(longitudinal_segments):
    ring_start = i * cross_section_segments
    next_ring_start = (i + 1) * cross_section_segments

    for j in range(cross_section_segments):
        nj = (j + 1) % cross_section_segments
        faces.append((
            ring_start + j,
            ring_start + nj,
            next_ring_start + nj,
            next_ring_start + j
        ))

# Cap both ends
start_center_index = len(vertices)
vertices.append((0.0, 0.0, -height * 0.5))

end_center_index = len(vertices)
vertices.append((0.0, 0.0, height * 0.5))

first_ring = 0
last_ring = longitudinal_segments * cross_section_segments

for j in range(cross_section_segments):
    nj = (j + 1) % cross_section_segments

    faces.append((start_center_index, first_ring + nj, first_ring + j))
    faces.append((end_center_index, last_ring + j, last_ring + nj))

# Create mesh
mesh = bpy.data.meshes.new("CoilSpringMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

# Create object
spring = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(spring)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Store useful construction metadata
spring["turns"] = turns
spring["centerline_radius"] = centerline_radius
spring["height"] = height
spring["wire_radius"] = wire_radius
