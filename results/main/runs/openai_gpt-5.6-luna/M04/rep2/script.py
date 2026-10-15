import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Torus knot parameters: (p, q) = (2, 3)
major_radius = 3.0
knot_radius = 1.2
tube_radius = 0.28

# Resolution: 256 longitudinal segments x 16 radial segments = 4096 quad faces
longitudinal_segments = 256
radial_segments = 16

def centerline(t):
    p = 2.0
    q = 3.0
    ct = math.cos(t)
    st = math.sin(t)
    cpt = math.cos(p * t)
    spt = math.sin(p * t)
    cqt = math.cos(q * t)
    sqt = math.sin(q * t)

    radial = major_radius + knot_radius * cqt
    return Vector((
        radial * cpt,
        radial * spt,
        knot_radius * sqt
    ))

def centerline_derivative(t):
    p = 2.0
    q = 3.0
    cpt = math.cos(p * t)
    spt = math.sin(p * t)
    cqt = math.cos(q * t)
    sqt = math.sin(q * t)

    radial = major_radius + knot_radius * cqt
    radial_derivative = -knot_radius * q * sqt

    return Vector((
        radial_derivative * cpt - radial * p * spt,
        radial_derivative * spt + radial * p * cpt,
        knot_radius * q * math.cos(q * t)
    ))

# Compute centerline points and Frenet-like frames
points = []
tangents = []
normals = []
binormals = []

for i in range(longitudinal_segments):
    t = 2.0 * math.pi * i / longitudinal_segments
    point = centerline(t)
    tangent = centerline_derivative(t).normalized()

    # Numerical derivative of the tangent for a stable normal
    dt = 1.0e-4
    tangent_before = centerline_derivative(t - dt).normalized()
    tangent_after = centerline_derivative(t + dt).normalized()
    tangent_derivative = (tangent_after - tangent_before) / (2.0 * dt)

    normal = tangent_derivative - tangent * tangent.dot(tangent_derivative)
    normal.normalize()
    binormal = tangent.cross(normal).normalized()

    points.append(point)
    tangents.append(tangent)
    normals.append(normal)
    binormals.append(binormal)

# Build swept tube mesh
vertices = []
faces = []

for i in range(longitudinal_segments):
    point = points[i]
    normal = normals[i]
    binormal = binormals[i]

    for j in range(radial_segments):
        angle = 2.0 * math.pi * j / radial_segments
        offset = tube_radius * (
            math.cos(angle) * normal +
            math.sin(angle) * binormal
        )
        vertices.append(tuple(point + offset))

for i in range(longitudinal_segments):
    next_i = (i + 1) % longitudinal_segments

    for j in range(radial_segments):
        next_j = (j + 1) % radial_segments

        a = i * radial_segments + j
        b = i * radial_segments + next_j
        c = next_i * radial_segments + next_j
        d = next_i * radial_segments + j

        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("TorusKnotTubeMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

obj = bpy.data.objects.new("TorusKnot_2_3_Tube", mesh)
bpy.context.collection.objects.link(obj)

# Smooth the tube surface
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Add weighted normals through smooth shading behavior without modifiers
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
