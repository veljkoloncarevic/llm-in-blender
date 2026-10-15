import bpy
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Spring parameters
turns = 8
coil_radius = 1.0
height = 4.0
wire_radius = 0.12

# Resolution: 512 longitudinal segments x 16 cross-section segments
longitudinal_segments = 512
cross_section_segments = 16

vertices = []
faces = []

# Vertical advance per radian
pitch_per_radian = height / (turns * 2.0 * math.pi)

# Build swept circular tube along the helical centerline
for i in range(longitudinal_segments + 1):
    t = i / longitudinal_segments
    theta = turns * 2.0 * math.pi * t

    c = math.cos(theta)
    s = math.sin(theta)

    center = Vector((
        coil_radius * c,
        coil_radius * s,
        height * t
    ))

    # Unit tangent of the helix
    tangent = Vector((
        -coil_radius * s,
        coil_radius * c,
        pitch_per_radian
    )).normalized()

    # Radial direction is perpendicular to the helix tangent
    radial = Vector((c, s, 0.0))

    # Complete orthonormal frame around the centerline
    binormal = tangent.cross(radial).normalized()

    for j in range(cross_section_segments):
        phi = 2.0 * math.pi * j / cross_section_segments
        offset = (
            radial * (wire_radius * math.cos(phi)) +
            binormal * (wire_radius * math.sin(phi))
        )
        vertices.append(tuple(center + offset))

# Connect adjacent cross-section rings
for i in range(longitudinal_segments):
    ring_a = i * cross_section_segments
    ring_b = (i + 1) * cross_section_segments

    for j in range(cross_section_segments):
        j_next = (j + 1) % cross_section_segments
        faces.append((
            ring_a + j,
            ring_a + j_next,
            ring_b + j_next,
            ring_b + j
        ))

# Add end-cap center vertices
start_center_index = len(vertices)
vertices.append((coil_radius, 0.0, 0.0))

end_center_index = len(vertices)
vertices.append((coil_radius, 0.0, height))

# Start cap
for j in range(cross_section_segments):
    j_next = (j + 1) % cross_section_segments
    faces.append((
        start_center_index,
        j_next,
        j
    ))

# End cap
end_ring = longitudinal_segments * cross_section_segments
for j in range(cross_section_segments):
    j_next = (j + 1) % cross_section_segments
    faces.append((
        end_center_index,
        end_ring + j,
        end_ring + j_next
    ))

# Create mesh object
mesh = bpy.data.meshes.new("CoilSpringMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

spring = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(spring)

# Smooth the swept tube
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Set the spring as the active object
bpy.context.view_layer.objects.active = spring
spring.select_set(True)
