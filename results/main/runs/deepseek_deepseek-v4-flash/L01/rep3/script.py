import bpy

# Remove all existing objects and orphan meshes
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

# Create tabletop: 2m x 1m x 0.1m, centered at z=1.0
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.0))
tabletop = bpy.context.object
tabletop.name = "Tabletop"
tabletop.scale = (1.0, 0.5, 0.05)

# Create four legs: each 0.1m x 0.1m x 1.0m, at table corners
leg_positions = [
    (0.9, 0.45),
    (0.9, -0.45),
    (-0.9, 0.45),
    (-0.9, -0.45),
]
for i, (x, y) in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.5))
    leg = bpy.context.object
    leg.name = f"Leg_{i+1}"
    leg.scale = (0.1, 0.1, 1.0)

# Add a low-segment bevel modifier to the tabletop
bevel_mod = tabletop.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.02
bevel_mod.segments = 1
