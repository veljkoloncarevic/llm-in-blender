import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gear parameters
teeth = 24
thickness = 0.3
root_radius = 1.0
tip_radius = 1.3
hole_radius = 0.35

# Six perimeter samples per tooth:
# root valley, rising flank, tooth top, tooth top, falling flank, root valley
tooth_offsets = (-0.48, -0.36, -0.18, 0.18, 0.36, 0.48)
tooth_radii = (root_radius, root_radius, tip_radius,
               tip_radius, root_radius, root_radius)

samples_per_tooth = len(tooth_offsets)
sample_count = teeth * samples_per_tooth
pitch = 2.0 * math.pi / teeth

vertices = []
faces = []

# Vertex rings:
# 0: bottom outer
# 1: top outer
# 2: bottom inner
# 3: top inner
rings = [[], [], [], []]

for i in range(sample_count):
    tooth_index = i // samples_per_tooth
    local_index = i % samples_per_tooth

    angle = tooth_index * pitch + tooth_offsets[local_index] * pitch
    radius = tooth_radii[local_index]

    ca = math.cos(angle)
    sa = math.sin(angle)

    rings[0].append(len(vertices))
    vertices.append((radius * ca, radius * sa, -thickness * 0.5))

    rings[1].append(len(vertices))
    vertices.append((radius * ca, radius * sa, thickness * 0.5))

    rings[2].append(len(vertices))
    vertices.append((hole_radius * ca, hole_radius * sa, -thickness * 0.5))

    rings[3].append(len(vertices))
    vertices.append((hole_radius * ca, hole_radius * sa, thickness * 0.5))

def add_quad(a, b, c, d):
    faces.append((a, b, c, d))

for i in range(sample_count):
    j = (i + 1) % sample_count

    bo_i, bo_j = rings[0][i], rings[0][j]
    to_i, to_j = rings[1][i], rings[1][j]
    bi_i, bi_j = rings[2][i], rings[2][j]
    ti_i, ti_j = rings[3][i], rings[3][j]

    # Top annular surface, upward-facing
    add_quad(ti_i, ti_j, to_j, to_i)

    # Bottom annular surface, downward-facing
    add_quad(bi_i, bo_i, bo_j, bi_j)

    # Outer perimeter wall
    add_quad(bo_i, bo_j, to_j, to_i)

    # Inner hole wall
    add_quad(bi_i, ti_i, ti_j, bi_j)

mesh = bpy.data.meshes.new("SpurGearMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

gear = bpy.data.objects.new("SpurGear_24T", mesh)
bpy.context.collection.objects.link(gear)

# Helpful object metadata
gear["teeth"] = teeth
gear["thickness"] = thickness
gear["hole_radius"] = hole_radius
gear["root_radius"] = root_radius
gear["tip_radius"] = tip_radius

# Set the gear as the active selected object
bpy.context.view_layer.objects.active = gear
gear.select_set(True)
