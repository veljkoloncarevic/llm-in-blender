import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
step_count = 24
angle_step = math.radians(15.0)
step_angle = math.radians(12.5)
inner_radius = 0.62
outer_radius = 2.20
step_thickness = 0.18
step_rise = 0.32
column_radius = 0.48
column_height = step_count * step_rise + 0.45
radial_segments = 5
angular_segments = 5

# Materials
def make_material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.metallic = metallic
    mat.roughness = roughness
    return mat

step_mat = make_material("Step Material", (0.18, 0.24, 0.32), 0.15, 0.32)
column_mat = make_material("Column Material", (0.10, 0.12, 0.15), 0.35, 0.28)
rail_mat = make_material("Handrail Material", (0.55, 0.30, 0.08), 0.65, 0.22)

# Central cylindrical column
bpy.ops.mesh.primitive_cylinder_add(
    vertices=48,
    radius=column_radius,
    depth=column_height,
    location=(0.0, 0.0, column_height * 0.5 - step_thickness * 0.5)
)
column = bpy.context.object
column.name = "Central Cylindrical Column"
column.data.materials.append(column_mat)

# Create a subdivided annular-sector step
def create_step(index):
    center_angle = index * angle_step
    a0 = center_angle - step_angle * 0.5
    a1 = center_angle + step_angle * 0.5
    z0 = index * step_rise
    z1 = z0 + step_thickness

    verts = []
    rings = 2
    layers = 2

    # Bottom and top vertex grids
    for z in (z0, z1):
        for ai in range(angular_segments + 1):
            t = ai / angular_segments
            angle = a0 + (a1 - a0) * t
            for ri in range(radial_segments + 1):
                r = inner_radius + (outer_radius - inner_radius) * ri / radial_segments
                verts.append((r * math.cos(angle), r * math.sin(angle), z))

    faces = []
    row_width = radial_segments + 1
    grid_size = (angular_segments + 1) * row_width

    # Top and bottom surfaces
    for layer in range(layers):
        base = layer * grid_size
        for ai in range(angular_segments):
            for ri in range(radial_segments):
                a = base + ai * row_width + ri
                b = a + 1
                c = a + row_width + 1
                d = a + row_width
                if layer == 0:
                    faces.append((a, d, c, b))
                else:
                    faces.append((a, b, c, d))

    # Outer and inner radial walls
    bottom_base = 0
    top_base = grid_size
    for ai in range(angular_segments):
        b0 = bottom_base + ai * row_width
        b1 = bottom_base + (ai + 1) * row_width
        t0 = top_base + ai * row_width
        t1 = top_base + (ai + 1) * row_width

        faces.append((b0, b1, t1, t0))

        b0o = b0 + radial_segments
        b1o = b1 + radial_segments
        t0o = t0 + radial_segments
        t1o = t1 + radial_segments
        faces.append((b0o, t0o, t1o, b1o))

    # Angular end walls
    for ri in range(radial_segments):
        b0 = bottom_base + ri
        b1 = b0 + 1
        t0 = top_base + ri
        t1 = t0 + 1
        faces.append((b0, t0, t1, b1))

        b0 = bottom_base + angular_segments * row_width + ri
        b1 = b0 + 1
        t0 = top_base + angular_segments * row_width + ri
        t1 = t0 + 1
        faces.append((b0, b1, t1, t0))

    mesh = bpy.data.meshes.new("Spiral Step Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(f"Spiral Step {index + 1:02d}", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(step_mat)

    bevel = obj.modifiers.new("Small Edge Bevel", 'BEVEL')
    bevel.width = 0.025
    bevel.segments = 2

    return obj

for i in range(step_count):
    create_step(i)

# Helical handrail as a polygonal tube following the outer edge
rail_radius = outer_radius + 0.10
rail_base_z = step_count * step_rise + 0.20
rail_height = 0.72
rail_samples = 145
tube_segments = 10
tube_radius = 0.065

rail_verts = []
rail_faces = []

for i in range(rail_samples):
    t = i / (rail_samples - 1)
    angle = t * (step_count - 1) * angle_step
    z = rail_base_z + t * (step_count - 1) * step_rise + rail_height

    center = Vector((
        rail_radius * math.cos(angle),
        rail_radius * math.sin(angle),
        z
    ))

    tangent = Vector((
        -rail_radius * math.sin(angle),
        rail_radius * math.cos(angle),
        (step_count - 1) * step_rise / ((step_count - 1) * angle_step)
    )).normalized()

    reference = Vector((0.0, 0.0, 1.0))
    normal = tangent.cross(reference).normalized()
    binormal = tangent.cross(normal).normalized()

    for j in range(tube_segments):
        phi = 2.0 * math.pi * j / tube_segments
        offset = tube_radius * (math.cos(phi) * normal + math.sin(phi) * binormal)
        rail_verts.append(tuple(center + offset))

for i in range(rail_samples - 1):
    for j in range(tube_segments):
        a = i * tube_segments + j
        b = i * tube_segments + (j + 1) % tube_segments
        c = (i + 1) * tube_segments + (j + 1) % tube_segments
        d = (i + 1) * tube_segments + j
        rail_faces.append((a, b, c, d))

# End caps
rail_faces.append(tuple(range(tube_segments - 1, -1, -1)))
last = (rail_samples - 1) * tube_segments
rail_faces.append(tuple(last + j for j in range(tube_segments)))

rail_mesh = bpy.data.meshes.new("Helical Handrail Mesh")
rail_mesh.from_pydata(rail_verts, [], rail_faces)
rail_mesh.update()

rail = bpy.data.objects.new("Outer Helical Handrail", rail_mesh)
bpy.context.collection.objects.link(rail)
rail.data.materials.append(rail_mat)

# Smooth the handrail
for poly in rail.data.polygons:
    poly.use_smooth = True

# Optional weighted smoothing for the column
for poly in column.data.polygons:
    poly.use_smooth = True
