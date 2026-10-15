import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gear parameters
tooth_count = 24
thickness = 0.3
root_radius = 1.0
outer_radius = 1.3
hole_radius = 0.35

# Angular profile samples for each tooth.
# The final boundary point is omitted because it is the first point
# of the following tooth sector.
profile_offsets = [-0.5, -0.40, -0.30, -0.22, 0.22, 0.30, 0.40]
profile_radii = [
    root_radius,
    root_radius,
    outer_radius,
    outer_radius,
    outer_radius,
    root_radius,
    root_radius,
]

pitch = (2.0 * math.pi) / tooth_count
profile = []

for tooth in range(tooth_count):
    tooth_center = tooth * pitch
    for offset, radius in zip(profile_offsets, profile_radii):
        angle = tooth_center + offset * pitch
        profile.append((angle, radius))

segment_count = len(profile)
half_thickness = thickness * 0.5

vertices = []

# Vertex layout:
# top outer, bottom outer, top inner, bottom inner
for angle, radius in profile:
    vertices.append((radius * math.cos(angle),
                     radius * math.sin(angle),
                     half_thickness))

for angle, radius in profile:
    vertices.append((radius * math.cos(angle),
                     radius * math.sin(angle),
                     -half_thickness))

for angle, radius in profile:
    vertices.append((hole_radius * math.cos(angle),
                     hole_radius * math.sin(angle),
                     half_thickness))

for angle, radius in profile:
    vertices.append((hole_radius * math.cos(angle),
                     hole_radius * math.sin(angle),
                     -half_thickness))

top_outer = 0
bottom_outer = segment_count
top_inner = segment_count * 2
bottom_inner = segment_count * 3

faces = []

for i in range(segment_count):
    j = (i + 1) % segment_count

    # Top annular surface
    faces.append((
        top_outer + i,
        top_outer + j,
        top_inner + j,
        top_inner + i
    ))

    # Bottom annular surface
    faces.append((
        bottom_outer + i,
        bottom_inner + i,
        bottom_inner + j,
        bottom_outer + j
    ))

    # Outer tooth perimeter
    faces.append((
        bottom_outer + i,
        bottom_outer + j,
        top_outer + j,
        top_outer + i
    ))

    # Inner hole perimeter
    faces.append((
        bottom_inner + i,
        top_inner + i,
        top_inner + j,
        bottom_inner + j
    ))

mesh = bpy.data.meshes.new("SpurGearMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

gear = bpy.data.objects.new("SpurGear_24T", mesh)
bpy.context.collection.objects.link(gear)

# Ensure consistent normals and clean mesh topology
bpy.context.view_layer.objects.active = gear
gear.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
gear.select_set(False)
