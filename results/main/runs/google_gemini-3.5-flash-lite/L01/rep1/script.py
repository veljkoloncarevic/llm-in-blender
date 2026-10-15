import bpy
import bmesh

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the low-poly table
table_width = 1.6
table_depth = 0.9
table_height = 0.75
top_thickness = 0.08
leg_width = 0.08
leg_inset = 0.1  # Distance from the edge of the tabletop to the outer edge of the leg

# -------------------------------------------------------------
# 1. Create Tabletop
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(
    size=1.0,
    location=(0, 0, table_height - top_thickness / 2)
)
tabletop = bpy.context.active_object
tabletop.name = "Tabletop"

# Scale cube to tabletop dimensions
tabletop.scale = (table_width, table_depth, top_thickness)

# Apply scale to ensure correct bevel behavior
bpy.ops.object.transform_apply(scale=True)

# Add Bevel modifier to tabletop for low-poly/smooth aesthetic
bevel_mod = tabletop.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.015
bevel_mod.segments = 2
bevel_mod.limit_method = 'ANGLE'
bevel_mod.angle_limit = 0.785398  # 45 degrees

# -------------------------------------------------------------
# 2. Create Legs (using a single joined mesh for efficiency)
# -------------------------------------------------------------
bm = bmesh.new()

# Calculate leg positions relative to origin
# Table ranges from -width/2 to width/2, etc.
x_offset = (table_width / 2) - leg_inset - (leg_width / 2)
y_offset = (table_depth / 2) - leg_inset - (leg_width / 2)
leg_height = table_height - top_thickness

leg_positions = [
    (x_offset, y_offset),
    (-x_offset, y_offset),
    (x_offset, -y_offset),
    (-x_offset, -y_offset)
]

for lx, ly in leg_positions:
    # Create a primitive cube bmesh for each leg
    leg_bm = bmesh.ops.create_cube(bm, size=1.0)
    
    # Scale and position the leg geometry
    bmesh.ops.scale(
        bm,
        verts=leg_bm['verts'],
        vec=(leg_width, leg_width, leg_height)
    )
    bmesh.ops.translate(
        bm,
        verts=leg_bm['verts'],
        vec=(lx, ly, leg_height / 2)
    )

# Create the mesh object for the legs
leg_mesh = bpy.data.meshes.new("TableLegs_Mesh")
bm.to_mesh(leg_mesh)
bm.free()

legs_obj = bpy.data.objects.new("TableLegs", leg_mesh)
bpy.context.collection.objects.link(legs_obj)

# -------------------------------------------------------------
# 3. Join Tabletop and Legs into a single low-poly table object
# -------------------------------------------------------------
# Select both and make tabletop active
bpy.ops.object.select_all(action='DESELECT')
tabletop.select_set(True)
legs_obj.select_set(True)
bpy.context.view_layer.objects.active = tabletop

bpy.ops.object.join()
tabletop.name = "LowPoly_Table"

# Final selection state
bpy.ops.object.select_all(action='DESELECT')
tabletop.select_set(True)
