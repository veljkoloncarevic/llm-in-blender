import bpy
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# (2,3) torus-knot parameters
p = 2
q = 3
major_radius = 3.0
minor_radius = 1.1
tube_radius = 0.28

# Resolution: 256 longitudinal segments x 16 cross-section segments = 4096 quad faces
longitudinal_segments = 256
cross_section_segments = 16

vertices = []
faces = []

def knot_position_and_tangent(t):
    pt = p * t
    qt = q * t
    cp = math.cos(pt)
    sp = math.sin(pt)
    cq = math.cos(qt)
    sq = math.sin(qt)

    radial_distance = major_radius + minor_radius * cq

    position = Vector((
        radial_distance * cp,
        radial_distance * sp,
        minor_radius * sq
    ))

    tangent = Vector((
        -minor_radius * q * sq * cp - p * radial_distance * sp,
        -minor_radius * q * sq * sp + p * radial_distance * cp,
        minor_radius * q * cq
    )).normalized()

    return position, tangent

# Build the swept tube
for i in range(longitudinal_segments):
    t = 2.0 * math.pi * i / longitudinal_segments
    position, tangent = knot_position_and_tangent(t)

    # Use the torus radial direction as a stable frame reference
    reference = Vector((math.cos(p * t), math.sin(p * t), 0.0))

    normal = reference - tangent * reference.dot(tangent)
    if normal.length < 1e-6:
        reference = Vector((0.0, 0.0, 1.0))
        normal = reference - tangent * reference.dot(tangent)

    normal.normalize()
    binormal = tangent.cross(normal).normalized()

    for j in range(cross_section_segments):
        angle = 2.0 * math.pi * j / cross_section_segments
        offset = (
            math.cos(angle) * normal +
            math.sin(angle) * binormal
        ) * tube_radius

        vertices.append(tuple(position + offset))

# Connect neighboring rings into a closed tube
for i in range(longitudinal_segments):
    next_i = (i + 1) % longitudinal_segments

    for j in range(cross_section_segments):
        next_j = (j + 1) % cross_section_segments

        a = i * cross_section_segments + j
        b = next_i * cross_section_segments + j
        c = next_i * cross_section_segments + next_j
        d = i * cross_section_segments + next_j

        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("TorusKnot_2_3_TubeMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

obj = bpy.data.objects.new("TorusKnot_2_3_Tube", mesh)
bpy.context.collection.objects.link(obj)

# Add a subtle bevel modifier for clean rounded normals without changing topology
weighted_normals = obj.modifiers.new("Weighted Normals", "WEIGHTED_NORMAL")
weighted_normals.keep_sharp = True
