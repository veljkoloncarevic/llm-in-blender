import bpy
import random
import mathutils

# --- CLEAN UP SCENE ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
# Shelf / Frame Material
mat_wood = bpy.data.materials.new(name="WoodMaterial")
mat_wood.use_nodes = True
mat_wood.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.15, 0.08, 0.03, 1.0) # Dark wood
mat_wood.node_tree.nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.5

# Book Colors (generate a few for variety)
book_colors = [
    (0.6, 0.1, 0.1, 1.0), # Red
    (0.1, 0.2, 0.5, 1.0), # Blue
    (0.1, 0.4, 0.1, 1.0), # Green
    (0.5, 0.4, 0.1, 1.0), # Gold
    (0.3, 0.1, 0.3, 1.0), # Purple
]

# --- BOOKSHELF FRAME ---
# Dimensions
width = 1.6
height = 2.2
depth = 0.4
thickness = 0.04

# Main Outer Box (using a cube scaled)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
frame = bpy.context.active_object
frame.name = "Bookshelf_Frame"
frame.scale = (width, depth, height)
bpy.ops.object.transform_apply(scale=True)
frame.data.materials.append(mat_wood)

# We want an open front. To keep geometry very simple and low poly, 
# let's carve out the inside using a boolean or just construct from slabs.
# Constructing from slabs is cleaner for low-poly:
bpy.ops.object.delete() # delete the solid cube, build modular panels

def create_panel(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

# Left Side
create_panel("Panel_Left", (-width/2 + thickness/2, 0, height/2), (thickness, depth, height), mat_wood)
# Right Side
create_panel("Panel_Right", (width/2 - thickness/2, 0, height/2), (thickness, depth, height), mat_wood)
# Top
create_panel("Panel_Top", (0, 0, height - thickness/2), (width, depth, thickness), mat_wood)
# Bottom
create_panel("Panel_Bottom", (0, 0, thickness/2), (width, depth, thickness), mat_wood)
# Back panel (thin)
create_panel("Panel_Back", (0, depth/2 - 0.01, height/2), (width - thickness*2, 0.02, height - thickness*2), mat_wood)

# Shelves (3 horizontal shelves inside)
# Total internal height = height - 2*thickness. Divide into 4 spaces -> 3 shelves.
num_shelves = 3
internal_height = height - (2 * thickness)
shelf_spacing = internal_height / (num_shelves + 1)

shelf_z_positions = []
for i in range(1, num_shelves + 1):
    z_pos = thickness + (i * shelf_spacing)
    shelf_z_positions.append(z_pos)
    create_panel(f"Shelf_{i}", (0, 0, z_pos), (width - (2*thickness), depth - 0.02, thickness), mat_wood)


# --- BOOKS VIA ARRAY MODIFIER ---
# Shelf inner width available for books
available_width = width - (2 * thickness) - 0.05
num_books_per_shelf = 12
book_width = available_width / num_books_per_shelf
book_height = shelf_spacing - 0.05  # slightly less than gap
book_depth = depth - 0.08

# Create a single master book for the array
for shelf_idx, sz in enumerate(shelf_z_positions):
    # Base book
    bpy.ops.mesh.primitive_cube_add(size=1, location=0)
    book = bpy.context.active_object
    book.name = f"Books_Shelf_{shelf_idx+1}"
    
    # Scale to book proportions (thin in X, tall in Z, deep in Y)
    # Pivot at bottom-left-back or center. Center is fine, we'll offset.
    bx = book_width * 0.85 # slightly smaller than slot to see separation
    by = book_depth
    bz = book_height * random.uniform(0.85, 1.0) # slight height variation per shelf
    
    book.scale = (bx, by, bz)
    bpy.ops.object.transform_apply(scale=True)
    
    # Assign unique material per shelf
    mat_book = bpy.data.materials.new(name=f"BookMat_{shelf_idx}")
    mat_book.use_nodes = True
    col = book_colors[shelf_idx % len(book_colors)]
    mat_book.node_nodes = mat_book.node_tree.nodes
    mat_book.node_nodes["Principled BSDF"].inputs['Base Color'].default_value = col
    mat_book.node_nodes["Principled BSDF"].inputs['Roughness'].default_value = 0.7
    book.data.materials.append(mat_book)
    
    # Position on shelf: start from left side of internal space
    start_x = -width/2 + thickness + 0.04 + (bx/2)
    start_y = 0.02 # push slightly back
    start_z = sz + (thickness/2) + (bz/2)
    
    book.location = (start_x, start_y, start_z)
    
    # Add Array Modifier
    array_mod = book.modifiers.new(name="BookArray", type='ARRAY')
    array_mod.count = num_books_per_shelf
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    # Offset along X axis by book_width
    array_mod.constant_offset_displace = (book_width * 1.02, 0, 0)
    
    # Optional: Add a tiny random displace or just leave clean array.
    # Array modifier keeps face count extremely low (12 cubes * 6 faces = 72 faces per shelf).

# Total face count is well under 2,000 faces (approx 15 cubes total in scene = 90 faces).
