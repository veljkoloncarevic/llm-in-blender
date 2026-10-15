import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused datablocks from the previous scene
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

def create_cube(name, location, dimensions):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

# Tabletop
tabletop = create_cube(
    "Tabletop",
    (0.0, 0.0, 2.2),
    (4.0, 2.4, 0.25)
)

# Low-poly bevel on the tabletop
bevel = tabletop.modifiers.new(name="Tabletop Bevel", type='BEVEL')
bevel.width = 0.08
bevel.segments = 1
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.523599  # 30 degrees

# Four square legs
leg_width = 0.30
leg_height = 2.1
leg_x = 1.65
leg_y = 0.85
leg_z = leg_height / 2.0

for index, (x, y) in enumerate((
    (-leg_x, -leg_y),
    (-leg_x,  leg_y),
    ( leg_x, -leg_y),
    ( leg_x,  leg_y),
), start=1):
    create_cube(
        f"Leg_{index}",
        (x, y, leg_z),
        (leg_width, leg_width, leg_height)
    )
