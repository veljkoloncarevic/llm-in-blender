import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helper to create a cube with applied dimensions
def create_cube(name, location, dimensions):
    bpy.ops.mesh.primitive_cube_add(
        size=1.0,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

# Table dimensions
table_width = 6.0
table_depth = 4.0
tabletop_thickness = 0.35
leg_height = 3.0
leg_size = 0.45

# Tabletop
tabletop = create_cube(
    "Tabletop",
    (0.0, 0.0, leg_height + tabletop_thickness / 2.0),
    (table_width, table_depth, tabletop_thickness)
)

# Bevel modifier on tabletop
bevel = tabletop.modifiers.new(name="Tabletop Bevel", type='BEVEL')
bevel.width = 0.12
bevel.segments = 1
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.5

# Four legs, inset slightly from tabletop edges
x_offset = table_width / 2.0 - leg_size
y_offset = table_depth / 2.0 - leg_size
leg_z = leg_height / 2.0

create_cube("Front Left Leg", (-x_offset, -y_offset, leg_z), (leg_size, leg_size, leg_height))
create_cube("Front Right Leg", (x_offset, -y_offset, leg_z), (leg_size, leg_size, leg_height))
create_cube("Back Left Leg", (-x_offset, y_offset, leg_z), (leg_size, leg_size, leg_height))
create_cube("Back Right Leg", (x_offset, y_offset, leg_z), (leg_size, leg_size, leg_height))
