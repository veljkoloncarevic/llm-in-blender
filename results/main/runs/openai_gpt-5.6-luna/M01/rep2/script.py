import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (
    bpy.data.meshes,
    bpy.data.curves,
    bpy.data.materials,
):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)

# Parameters
step_count = 24
angle_step = math.radians(15.0)
step_rise = 0.24
step_thickness = 0.22
inner_radius = 0.72
outer_radius = 3.0
step_half_angle = math.radians(6.5)
arc_segments = 8

column_radius = 0.62
column_height = step_count * step_rise + 0.55

rail_radius = outer_radius + 0.10
rail_clearance = 1.05
rail_tube_radius = 0.075
rail_segments = step_count * 8

# Materials
def make_material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    return mat

step_mat = make_material("Step Material", (0.24, 0.12, 0.055), 0.05, 0.38)
column_mat = make_material("Central Column", (0.16, 0.18, 0.21), 0.25, 0.3)
rail_mat = make_material("Handrail", (0.08, 0.09, 0.11), 0.65, 0.22)

# Create one solid wedge-shaped stair step
def create_step(index):
    z_bottom = index * step_rise
    z_top = z_bottom + step_thickness
    rotation = index * angle_step

    boundary = []

    # Outer curved edge
    for i in range(arc_segments + 1):
        a = -step_half_angle + (2.0 * step_half_angle) * i / arc_segments
        boundary.append((outer_radius * math.cos(a),
                         outer_radius * math.sin(a)))

    # Inner curved edge, reversed
    for i in range(arc_segments, -1, -1):
        a = -step_half_angle + (2.0 * step_half_angle) * i / arc_segments
        boundary.append((inner_radius * math.cos(a),
                         inner_radius * math.sin(a)))

    n = len(boundary)
    vertices = []
    for x, y in boundary:
        vertices.append((x, y, z_bottom))
    for x, y in boundary:
        vertices.append((x, y, z_top))

    faces = []

    # Bottom and top
    faces.append(tuple(range(n - 1, -1, -1)))
    faces.append(tuple(range(n, 2 * n)))

    # Perimeter walls
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))

    mesh = bpy.data.meshes.new(f"StairStep_{index + 1:02d}")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(f"Stair Step {index + 1:02d}", mesh)
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler[2] = rotation
    obj.data.materials.append(step_mat)

    # Small bevel for readable edges
    bevel = obj.modifiers.new("Soft Step Edges", 'BEVEL')
    bevel.width = 0.035
    bevel.segments = 2
    bevel.limit_method = 'ANGLE'

    return obj

for i in range(step_count):
    create_step(i)

# Central cylindrical column
bpy.ops.mesh.primitive_cylinder_add(
    vertices=48,
    radius=column_radius,
    depth=column_height,
    location=(0.0, 0.0, column_height * 0.5 - 0.12)
)
column = bpy.context.object
column.name = "Central Cylindrical Column"
column.data.materials.append(column_mat)

column_bevel = column.modifiers.new("Column Edge Softening", 'BEVEL')
column_bevel.width = 0.035
column_bevel.segments = 2

# Helical outer handrail
curve_data = bpy.data.curves.new("Helical Handrail Curve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 1
curve_data.bevel_depth = rail_tube_radius
curve_data.bevel_resolution = 4
curve_data.resolution_u = 2

spline = curve_data.splines.new('POLY')
spline.points.add(rail_segments)

for i in range(rail_segments + 1):
    t = i / rail_segments
    angle = t * step_count * angle_step
    z = (t * (step_count - 1) * step_rise) + step_thickness + rail_clearance

    spline.points[i].co = (
        rail_radius * math.cos(angle),
        rail_radius * math.sin(angle),
        z,
        1.0
    )

rail = bpy.data.objects.new("Continuous Helical Handrail", curve_data)
bpy.context.collection.objects.link(rail)
curve_data.materials.append(rail_mat)

# Add compact vertical end posts tying the handrail into the first and last steps
post_radius = rail_tube_radius * 0.9
post_depth = rail_clearance + 0.2

for label, angle, base_z in (
    ("Lower Handrail Post", 0.0, step_thickness),
    ("Upper Handrail Post", step_count * angle_step, 
     (step_count - 1) * step_rise + step_thickness),
):
    x = rail_radius * math.cos(angle)
    y = rail_radius * math.sin(angle)

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20,
        radius=post_radius,
        depth=post_depth,
        location=(x, y, base_z + post_depth * 0.5)
    )
    post = bpy.context.object
    post.name = label
    post.data.materials.append(rail_mat)

# Set useful object display settings
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for polygon in obj.data.polygons:
            polygon.use_smooth = False
    elif obj.type == 'CURVE':
        obj.data.resolution_u = 2
