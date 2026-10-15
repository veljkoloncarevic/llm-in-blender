import bpy
import bmesh

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Collection for the table
collection = bpy.context.scene.collection

# 1. Create Tabletop
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.8))
tabletop = bpy.context.active_object
tabletop.name = "Tabletop"

# Scale tabletop to be rectangular and thin (e.g., 2.0 x 1.2 x 0.1)
tabletop.scale = (2.0, 1.2, 0.1)
bpy.ops.object.transform_apply(scale=True)

# Add Bevel modifier to tabletop
bevel_mod = tabletop.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.02
bevel_mod.segments = 2
bevel_mod.limit_method = 'ANGLE'

# 2. Create Table Legs
# Tabletop dimensions: X = 2.0, Y = 1.2, Top Z = 1.8 + 0.05 = 1.85
# Let's place legs near the corners, inset slightly.
leg_height = 1.75
leg_size = 0.1
leg_z_loc = leg_height / 2.0

x_offset = 0.85
y_offset = 0.45

leg_positions = [
    (x_offset, y_offset, leg_z_loc),
    (-x_offset, y_offset, leg_z_loc),
    (x_offset, -y_offset, leg_z_loc),
    (-x_offset, -y_offset, leg_z_loc),
]

# Create a single mesh for all legs to keep geometry unified and low-poly
bm = bmesh.new()

for pos in leg_positions:
    # Create a primitive cube for each leg using bmesh
    bmesh.ops.create_cube(bm, size=1.0)
    
    # Transform each leg into position and scale
    matrix = mathutils.Matrix.Translation(pos) @ mathutils.Matrix.Scale(leg_size, 4, (1,0,0)) @ mathutils.Matrix.Scale(leg_size, 4, (0,1,0)) @ mathutils.Matrix.Scale(leg_height, 4, (0,0,1))
    # Wait, simpler to transform vertex coordinates directly or use transform:
    # Let's just use transform on the newly added geometry or create primitive with matrix.
    # Actually, bmesh.ops.create_cube doesn't take matrix directly, but we can transform the whole bm at the end or per-cube.
    
# Better approach: loop and use primitive_cube_add for simplicity, then join them
leg_objects = []
for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=pos)
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    leg.scale = (leg_size, leg_size, leg_height)
    bpy.ops.object.transform_apply(scale=True)
    leg_objects.append(leg)

# Select all legs and join them into one object
bpy.ops.object.select_all(action='DESELECT')
for leg in leg_objects:
    leg.select_set(True)
bpy.context.view_layer.objects.active = leg_objects[0]
bpy.ops.object.join()
legs_merged = bpy.context.active_object
legs_merged.name = "Table_Legs"

# Combine Tabletop and Legs into a single low-poly table object (optional, but clean)
tabletop.select_set(True)
legs_merged.select_set(True)
bpy.context.view_layer.objects.active = tabletop
bpy.ops.object.join()
tabletop.name = "LowPoly_Table"

# Final clean-up / shade smooth low-poly style
bpy.ops.object.shade_flat()

print("Low-poly table created successfully.")
