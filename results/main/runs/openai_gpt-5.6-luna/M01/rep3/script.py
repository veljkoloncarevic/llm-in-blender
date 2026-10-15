import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_material(name, color, metallic=0.0, roughness=0.45):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.metallic = metallic
    mat.roughness = roughness
    return mat

step_mat = make_material("Step Material", (0.22, 0.28, 0.34), 0.15, 0.32)
column_mat = make_material("Column Material", (0.12, 0.14, 0.17), 0.25, 0.28)
rail_mat = make_material("Handrail Material", (0.55, 0.25, 0.07), 0.65, 0.24)

# Staircase parameters
step_count = 24
step_angle = math.radians(15.0)
step_rise = 0.42
step_width_radial = 2.55
step_depth_tangential = 1.18
step_thickness = 0.32
step_center_radius = 1.72
first_step_z = 0.18

# Central cylindrical column
column_height = first_step_z + step_count * step_rise + 0.9
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=0.58,
    depth=column_height,
    location=(0.0, 0.0, column_height * 0.5 - 0.25)
)
column = bpy.context.object
column.name = "Central Cylindrical Column"
column.data.materials.append(column_mat)

column_bevel = column.modifiers.new("Subtle Column Edge Bevel", 'BEVEL')
column_bevel.width = 0.055
column_bevel.segments = 3
column_bevel.limit_method = 'ANGLE'
bpy.context.view_layer.objects.active = column
bpy.ops.object.modifier_apply(modifier=column_bevel.name)

# Stair steps
for i in range(step_count):
    angle = i * step_angle
    radius = step_center_radius
    z = first_step_z + i * step_rise

    x = radius * math.cos(angle)
    y = radius * math.sin(angle)

    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=(x, y, z),
        rotation=(0.0, 0.0, angle)
    )
    step = bpy.context.object
    step.name = f"Step_{i + 1:02d}"
    step.dimensions = (
        step_width_radial,
        step_depth_tangential,
        step_thickness
    )
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    step.data.materials.append(step_mat)

    bevel = step.modifiers.new("Rounded Step Edges", 'BEVEL')
    bevel.width = 0.075
    bevel.segments = 3
    bevel.limit_method = 'ANGLE'

    bpy.context.view_layer.objects.active = step
    bpy.ops.object.modifier_apply(modifier=bevel.name)

# Helical outer handrail
rail_radius = step_center_radius + step_width_radial * 0.5 + 0.10
rail_base_height = first_step_z + step_thickness * 0.5 + 0.78
rail_top_height = rail_base_height + (step_count - 1) * step_rise

curve_data = bpy.data.curves.new("Helical Handrail Curve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 2
curve_data.bevel_depth = 0.095
curve_data.bevel_resolution = 4
curve_data.resolution_u = 2
curve_data.use_fill_caps = True

spline = curve_data.splines.new('POLY')
samples_per_step = 12
sample_count = (step_count - 1) * samples_per_step + 1
spline.points.add(sample_count - 1)

for j in range(sample_count):
    t = j / (sample_count - 1)
    angle = t * (step_count - 1) * step_angle
    z = rail_base_height + t * (rail_top_height - rail_base_height)

    x = rail_radius * math.cos(angle)
    y = rail_radius * math.sin(angle)
    spline.points[j].co = (x, y, z, 1.0)

rail = bpy.data.objects.new("Continuous Helical Handrail", curve_data)
bpy.context.collection.objects.link(rail)
curve_data.materials.append(rail_mat)

# Add slim vertical supports beneath the handrail at every step
for i in range(step_count):
    angle = i * step_angle
    x = rail_radius * math.cos(angle)
    y = rail_radius * math.sin(angle)
    step_z = first_step_z + i * step_rise + step_thickness * 0.5
    rail_z = rail_base_height + i * step_rise
    support_height = rail_z - step_z

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=20,
        radius=0.045,
        depth=support_height,
        location=(x, y, step_z + support_height * 0.5)
    )
    support = bpy.context.object
    support.name = f"Handrail_Support_{i + 1:02d}"
    support.data.materials.append(rail_mat)

# Smooth shading for cylindrical components
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH' and (
        "Column" in obj.name or
        "Support" in obj.name
    ):
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
