import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gear parameters
tooth_count = 24
root_radius = 2.0
outer_radius = 2.5
hole_radius = 0.7
thickness = 0.3

# Six boundary points per tooth:
# root valley, root shoulder, outer flank, outer flank, root shoulder, root valley
profile = [
    (-0.50, root_radius),
    (-0.34, root_radius),
    (-0.22, outer_radius),
    ( 0.22, outer_radius),
    ( 0.34, root_radius),
    ( 0.50, root_radius),
]

points_per_tooth = len(profile)
boundary_count = tooth_count * points_per_tooth
half_thickness = thickness * 0.5

vertices = []
faces = []

# Vertex indexing helpers
def outer_bottom(i):
    return i

def outer_top(i):
    return boundary_count + i

def inner_bottom(i):
    return boundary_count * 2 + i

def inner_top(i):
    return boundary_count * 3 + i

# Create corresponding outer and inner rings
for tooth in range(tooth_count):
    tooth_angle = 2.0 * math.pi * tooth / tooth_count
    for local_angle, radius in profile:
        angle = tooth_angle + local_angle * (2.0 * math.pi / tooth_count)
        vertices.append((radius * math.cos(angle),
                         radius * math.sin(angle),
                         -half_thickness))

for tooth in range(tooth_count):
    tooth_angle = 2.0 * math.pi * tooth / tooth_count
    for local_angle, radius in profile:
        angle = tooth_angle + local_angle * (2.0 * math.pi / tooth_count)
        vertices.append((radius * math.cos(angle),
                         radius * math.sin(angle),
                         half_thickness))

# Inner hole rings use the same angular sampling as the outer boundary
for z in (-half_thickness, half_thickness):
    for i in range(boundary_count):
        tooth = i // points_per_tooth
        local_index = i % points_per_tooth
        local_angle = profile[local_index][0]
        angle = (2.0 * math.pi * tooth / tooth_count +
                 local_angle * (2.0 * math.pi / tooth_count))
        vertices.append((hole_radius * math.cos(angle),
                         hole_radius * math.sin(angle),
                         z))

# Build annular top and bottom surfaces
for i in range(boundary_count):
    j = (i + 1) % boundary_count

    # Top annulus, upward-facing
    faces.append((
        outer_top(i),
        outer_top(j),
        inner_top(j),
        inner_top(i),
    ))

    # Bottom annulus, downward-facing
    faces.append((
        outer_bottom(j),
        outer_bottom(i),
        inner_bottom(i),
        inner_bottom(j),
    ))

    # Outer perimeter walls
    faces.append((
        outer_bottom(i),
        outer_bottom(j),
        outer_top(j),
        outer_top(i),
    ))

    # Hole walls, facing inward
    faces.append((
        inner_bottom(i),
        inner_top(i),
        inner_top(j),
        inner_bottom(j),
    ))

# Create the single mesh object
mesh = bpy.data.meshes.new("SpurGearMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

gear = bpy.data.objects.new("SpurGear_24T", mesh)
bpy.context.collection.objects.link(gear)

# Smooth only the hole and outer wall transitions are unnecessary;
# keep the gear's machined faces flat and clearly defined.
for polygon in mesh.polygons:
    polygon.use_smooth = False

# Set the object as active
bpy.context.view_layer.objects.active = gear
gear.select_set(True)
