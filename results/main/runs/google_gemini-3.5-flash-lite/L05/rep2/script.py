import bpy
import random
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set random seed for reproducibility
random.seed(42)

# --- MATERIALS ---
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].setDefaultValue(color)
        bsdf.inputs['Roughness'].setDefaultValue(0.4)
    return mat

wood_mat = create_material("Wood", (0.15, 0.08, 0.03, 1.0))
book_colors = [
    create_material("Book_Red", (0.5, 0.05, 0.05, 1.0)),
    create_material("Book_Blue", (0.05, 0.15, 0.4, 1.0)),
    create_material("Book_Green", (0.05, 0.3, 0.1, 1.0)),
    create_material("Book_Yellow", (0.6, 0.4, 0.05, 1.0)),
    create_material("Book_Dark", (0.1, 0.1, 0.1, 1.0))
]

# --- BOOKSHELF FRAME ---
# Dimensions
width = 1.2
height = 1.8
depth = 0.35
thickness = 0.03

# Create main box frame using a cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height/2))
frame = bpy.context.active_object
frame.name = "Bookshelf_Frame"
frame.scale = (width, depth, height)
bpy.ops.object.transform_apply(scale=True)
frame.data.materials.append(wood_mat)

# Carve out the inside to make it a shell (simulate thin walls/shelves)
# Instead of complex booleans which add high polycount, let's build from thin cubes 
# to keep face count strictly low and clean.
bpy.ops.object.delete()

# Build frame from primitive thin boxes
def add_box(name, loc, scale, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

# Left Side
add_box("Frame_Left", (-width/2 + thickness/2, 0, height/2), (thickness, depth, height), wood_mat)
# Right Side
add_box("Frame_Right", (width/2 - thickness/2, 0, height/2), (thickness, depth, height), wood_mat)
# Top
add_box("Frame_Top", (0, 0, height - thickness/2), (width, depth, thickness), wood_mat)
# Bottom
add_box("Frame_Bottom", (0, 0, thickness/2), (width, depth, thickness), wood_mat)
# Back panel (very thin)
add_box("Frame_Back", (0, depth/2 - 0.005, height/2), (width - thickness*2, 0.01, height - thickness*2), wood_mat)

# Shelves (3 horizontal shelves: bottom, middle, upper-middle)
shelf_heights = [height * 0.25, height * 0.55, height * 0.825]
shelf_width = width - (thickness * 2)
shelf_depth = depth - 0.02

for i, sh in enumerate(shelf_heights):
    add_box(f"Shelf_{i+1}", (0, 0.01, sh), (shelf_width, shelf_depth, thickness), wood_mat)


# --- BOOKS (Using Array Modifier) ---
# Shelf inner width is approx width - 2*thickness = 1.14
# We want at least 10 books per shelf. Let's make 12 books per row.
num_books = 12
available_width = width - 0.08
book_thickness = available_width / num_books

for i, sh in enumerate(shelf_heights):
    # Base book for the array
    # Randomize dimensions slightly per shelf via scale, or keep uniform for array
    b_width = book_thickness * 0.85
    b_height = random.uniform(0.22, 0.30)
    b_depth = random.uniform(0.22, 0.28)
    
    # Position first book on the left of the shelf
    start_x = -width/2 + thickness + b_width/2 + 0.02
    start_z = sh + thickness/2 + b_height/2
    start_y = 0.02  # Push slightly back from shelf edge
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=(start_x, start_y, start_z))
    book = bpy.context.active_object
    book.name = f"Shelf_{i+1}_Book"
    book.scale = (b_width, b_depth, b_height)
    bpy.ops.object.transform_apply(scale=True)
    
    # Assign random book material
    book.data.materials.append(random.choice(book_colors))
    
    # Add Array Modifier
    array_mod = book.modifiers.new(name="BookArray", type='ARRAY')
    array_mod.count = num_books
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace = (book_thickness, 0, 0)
    
    # Optional: Add a slight variation/gap using a second object or just keep clean array.
    # To keep face count super low, a simple array of 6-sided cubes (6 faces each) 
    # 3 shelves * 12 books * 6 faces = 216 faces for books. Extremely optimized!

# Shade smooth/flat appropriately across all mesh objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons:
            poly.use_smooth = False
