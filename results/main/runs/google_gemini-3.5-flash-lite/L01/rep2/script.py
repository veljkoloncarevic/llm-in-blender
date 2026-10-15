import bpy
import bmesh
from mathutils import Vector

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Create Tabletop Mesh
mesh_top = bpy.data.meshes.new("Tabletop_Mesh")
obj_top = bpy.data.objects.new("Tabletop", mesh_top)
bpy.context.collection.objects.link(obj_top)

bm_top = bmesh.new()
# Dimensions: X=1.6, Y=1.0, Z=0.1
bmesh.ops.create_cube(bm_top, size=1.0)
# Scale it to be a rectangular tabletop
bmesh.ops.scale(bm_top, vec=Vector((1.6, 1.0, 0.1)), verts=bm_top.verts)
# Position it above the origin
bmesh.ops.translate(bm_top, vec=Vector((0, 0, 0.95)), verts=bm_top.verts)
bm_top.to_mesh(mesh_top)
bm_top.free()

# Add a Bevel modifier to the tabletop for a clean low-poly look
bevel_mod = obj_top.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.02
bevel_mod.segments = 2
bevel_mod.limit_method = 'ANGLE'

# 3. Create Table Legs (Single Mesh for efficiency)
mesh_legs = bpy.data.meshes.new("TableLegs_Mesh")
obj_legs = bpy.data.objects.new("TableLegs", mesh_legs)
bpy.context.collection.objects.link(obj_legs)

bm_legs = bmesh.new()

# Define leg dimensions and offset from center
leg_size_x = 0.1
leg_size_y = 0.1
leg_height = 0.9
leg_z_pos = leg_height / 2.0

# Offsets in X and Y to place legs near the corners of the 1.6x1.0 tabletop
x_offset = (1.6 / 2.0) - 0.12
y_offset = (1.0 / 2.0) - 0.12

offsets = [
    Vector(( x_offset,  y_offset, leg_z_pos)),
    Vector((-x_offset,  y_offset, leg_z_pos)),
    Vector(( x_offset, -y_offset, leg_z_pos)),
    Vector((-x_offset, -y_offset, leg_z_pos))
]

for pos in offsets:
    # Create a primitive cube for each leg
    leg_bm = bmesh.new()
    bmesh.ops.create_cube(leg_bm, size=1.0)
    # Scale to leg proportions (thin and tall)
    bmesh.ops.scale(leg_bm, vec=Vector((leg_size_x, leg_size_y, leg_height)), verts=leg_bm.verts)
    # Translate to position
    bmesh.ops.translate(leg_bm, vec=pos, verts=leg_bm.verts)
    
    # Merge into the main leg bmesh
    for v in leg_bm.verts:
        bm_legs.verts.new(v.co)
    bm_legs.verts.ensure_lookup_table()
    
    for f in leg_bm.faces:
        try:
            bm_legs.faces.new([bm_legs.verts[i.index] for i in f.verts])
        except ValueError:
            pass # Skip if face already exists (shouldn't happen here)
            
    leg_bm.free()

bm_legs.to_mesh(mesh_legs)
bm_legs.free()

# 4. Apply smooth shading / finalize
for obj in [obj_top, obj_legs]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
