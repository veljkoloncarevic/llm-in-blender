import bpy
import random
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Dimensions
shelf_width = 2.0
shelf_height = 1.8
shelf_depth = 0.4
thickness = 0.04

# 1. Create Bookshelf Frame
# Frame uses a cube scaled to dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, shelf_height / 2))
frame = bpy.active_object
frame.name = "Bookshelf_Frame"

# We'll use a procedural approach with a single mesh for the frame to keep polycount ultra-low
import bmesh
bm = bmesh.new()

# Helper to add a box to the bmesh
def add_box(bm, loc, scale):
    mat = mathutils.Matrix.Translation(loc) @ mathutils.Matrix.Scale(scale[0], 4, mathutils.Vector((1,0,0))) @ mathutils.Matrix.Scale(scale[1], 4, mathutils.Vector((0,1,0))) @ mathutils.Matrix.Scale(scale[2], 4, mathutils.Vector((0,0,1)))
    # Create cube manually via bmesh
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

# Clear default cube data from the primitive operator
bm.from_mesh(frame.data)
bm.clear()

# Frame pieces: Left side, Right side, Top, Bottom, Back panel
# Left Side
add_box(bm, (-shelf_width/2 + thickness/2, 0, shelf_height/2), (thickness, shelf_depth, shelf_height))
# Right Side
add_box(bm, (shelf_width/2 - thickness/2, 0, shelf_height/2), (thickness, shelf_depth, shelf_height))
# Top
add_box(bm, (0, 0, shelf_height - thickness/2), (shelf_width, shelf_depth, thickness))
# Bottom
add_box(bm, (0, 0, thickness/2), (shelf_width, shelf_depth, thickness))
# Back Panel (thin)
back_thick = 0.01
add_box(bm, (0, shelf_depth/2 - back_thick/2, shelf_height/2), (shelf_width - thickness*2, back_thick, shelf_height - thickness*2))

# Shelves (2 intermediate shelves)
num_shelves = 3 # bottom, middle1, middle2, top (so 2 intermediate)
for i in range(1, 3):
    z_pos = (shelf_height / 3) * i
    add_box(bm, (0, 0, z_pos), (shelf_width - thickness*2, shelf_depth - 0.02, thickness))

bm.to_mesh(frame.data)
bm.free()

# 2. Create Books via Array Modifier
# Shelf heights to populate
# Bottom shelf sits on z = thickness, top of shelf is thickness
# Intermediates are at height/3 and 2*height/3
shelf_z_levels = [
    thickness,
    (shelf_height / 3),
    (shelf_height / 3) * 2
]

book_depth = shelf_depth - 0.05
book_height = (shelf_height / 3) - thickness - 0.05

for idx, z_base in enumerate(shelf_z_levels):
    # Create base book
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    book = bpy.active_object
    book.name = f"Book_Shelf_{idx}"
    
    # Scale book to thin proportions (along X is width, Y is depth, Z is height)
    # Unit cube is 1x1x1. Let's make a single book: width=0.04, depth=book_depth, height=book_height
    # We want variation per shelf, so let's scale in object mode
    b_width = 0.035
    b_depth = book_depth * random.uniform(0.8, 1.0)
    b_height = book_height * random.uniform(0.75, 0.95)
    
    book.scale = (b_width, b_depth, b_height)
    bpy.ops.object.transform_apply(scale=True)
    
    # Move origin to bottom-left-back or similar for better array alignment, 
    # but center origin is fine if we offset correctly.
    # Center of book is at origin of object.
    # Place it on the shelf:
    # X start: left side + padding + half width
    start_x = -shelf_width/2 + thickness + b_width/2 + 0.02
    # Y pos: slightly pushed back from front edge
    y_pos = 0.02 # relative to center of shelf depth
    # Z pos: shelf bottom + half height
    z_pos = z_base + thickness/2 + b_height/2
    
    book.location = (start_x, y_pos, z_pos)
    
    # Add Array Modifier
    array_mod = book.modifiers.new(name="BookArray", type='ARRAY')
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    
    # Gap between books (slight random offset simulated by constant spacing slightly larger than width)
    # To make them look slightly organic, we use a fixed distance
    array_mod.constant_offset_displace = (b_width + 0.005, 0.0, 0.0)
    
    # Count to fill roughly the shelf width (shelf_width - margins)
    available_width = shelf_width - (thickness * 2) - 0.08
    count = int(available_width / (b_width + 0.005))
    array_mod.count = max(count, 10) # ensure at least 10

# Final scene check:
# Frame: ~14 cubes * 6 faces = 84 faces
# Books: 3 base books with arrays of ~15 each = 45 books * 6 faces = 270 faces
# Total faces well under 2,000.
