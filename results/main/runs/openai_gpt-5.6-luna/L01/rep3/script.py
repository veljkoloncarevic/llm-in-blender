import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the rectangular tabletop
bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 2.2))
tabletop = bpy.context.object
tabletop.name = "Tabletop"
tabletop.dimensions = (6.0, 4.0, 0.35)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add a low-poly bevel modifier to the tabletop
bevel = tabletop.modifiers.new(name="Tabletop Bevel", type='BEVEL')
bevel.width = 0.12
bevel.segments = 1
bevel.profile = 0.5
bevel.limit_method = 'ANGLE'

# Create four legs
leg_positions = [
    (-2.55, -1.55),
    (-2.55,  1.55),
    ( 2.55, -1.55),
    ( 2.55,  1.55),
]

for index, (x, y) in enumerate(leg_positions, start=1):
    bpy.ops.mesh.primitive_cube_add(location=(x, y, 1.05))
    leg = bpy.context.object
    leg.name = f"Leg_{index}"
    leg.dimensions = (0.45, 0.45, 2.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
