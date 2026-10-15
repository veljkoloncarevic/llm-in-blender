import bpy
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Torus knot parameters: (p, q) = (2, 3)
p = 2
q = 3
major_radius = 2.0
minor_radius = 0.8
tube_radius = 0.22

# Resolution: 256 longitudinal segments x 16 circular segments = 4096 quad faces
curve_segments = 256
cross_segments = 16

vertices = []
faces = []

for i in range(curve_segments):
    t = 2.0 * math.pi * i / curve_segments
    pt = p * t
    qt = q * t

    cqt = math.cos(qt)
    sqt = math.sin(qt)
    cpt = math.cos(pt)
    spt = math.sin(pt)

    radial_distance = major_radius + minor_radius * cqt

    # Parametric torus knot centerline
    center = Vector((
        radial_distance * cpt,
        radial_distance * spt,
        minor_radius * sqt
    ))

    # Analytic tangent derivative
    tangent = Vector((
        -minor_radius * q * sqt * cpt - radial_distance * p * spt,
        -minor_radius * q * sqt * spt + radial_distance * p * cpt,
        minor_radius * q * cqt
    )).normalized()

    # Use the outward direction from the torus axis as a stable frame reference
    reference = Vector((cpt, spt, 0.0))
    normal = reference - tangent * reference.dot(tangent)

    if normal.length < 1e-6:
        reference = Vector((0.0, 0.0, 1.0))
        normal = reference - tangent * reference.dot(tangent)

    normal.normalize()
    binormal = tangent.cross(normal).normalized()

    # Circular tube cross-section
    for j in range(cross_segments):
        angle = 2.0 * math.pi * j / cross_segments
        offset = (
            math.cos(angle) * normal +
            math.sin(angle) * binormal
        ) * tube_radius
        vertices.append(tuple(center + offset))

# Connect neighboring rings, including the closing seam
for i in range(curve_segments):
    next_i = (i + 1) % curve_segments
    for j in range(cross_segments):
        next_j = (j + 1) % cross_segments

        a = i * cross_segments + j
        b = i * cross_segments + next_j
        c = next_i * cross_segments + next_j
        d = next_i * cross_segments + j

        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("TorusKnot_2_3_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

obj = bpy.data.objects.new("TorusKnot_2_3", mesh)
bpy.context.collection.objects.link(obj)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True
