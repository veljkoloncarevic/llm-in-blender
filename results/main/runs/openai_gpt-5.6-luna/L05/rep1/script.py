import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    if datablocks != bpy.data.materials:
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

# Materials
def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

frame_mat = make_material("Dark Wood", (0.16, 0.055, 0.025))
shelf_mat = make_material("Shelf Wood", (0.28, 0.10, 0.035))
book_mats = [
    make_material("Books Red", (0.55, 0.045, 0.035)),
    make_material("Books Blue", (0.035, 0.16, 0.48)),
    make_material("Books Green", (0.06, 0.36, 0.14)),
]

def add_cube(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj

# Overall bookshelf dimensions:
# Width: 8 units, height: 8 units, depth: 2 units
# Side panels
add_cube("Left Side", (-3.85, 0.0, 0.0), (0.30, 2.0, 7.6), frame_mat)
add_cube("Right Side", (3.85, 0.0, 0.0), (0.30, 2.0, 7.6), frame_mat)

# Top and bottom of the box frame
add_cube("Top Frame", (0.0, 0.0, 3.85), (7.7, 2.0, 0.30), frame_mat)
add_cube("Bottom Frame", (0.0, 0.0, -3.85), (7.7, 2.0, 0.30), frame_mat)

# Thin rear panel
add_cube("Back Panel", (0.0, 0.92, 0.0), (7.7, 0.16, 7.6), frame_mat)

# Three horizontal shelves
shelf_z_positions = (-2.70, -0.30, 2.10)
for index, z in enumerate(shelf_z_positions, start=1):
    add_cube(
        f"Shelf {index}",
        (0.0, 0.0, z),
        (7.7, 1.9, 0.18),
        shelf_mat
    )

# Add one source book per shelf, then use an Array modifier to create 10 books.
# The transforms are applied before adding the modifier so relative spacing is reliable.
book_specs = [
    ("Lower", -2.70, 1.75, book_mats[0]),
    ("Middle", -0.30, 1.80, book_mats[1]),
    ("Upper",  2.10, 1.35, book_mats[2]),
]

for label, shelf_z, book_height, material in book_specs:
    shelf_top = shelf_z + 0.09
    book_width = 0.53
    book_depth = 1.48
    first_x = -3.35
    book_center_z = shelf_top + book_height * 0.5

    book = add_cube(
        f"{label} Book Source",
        (first_x, -0.08, book_center_z),
        (book_width, book_depth, book_height),
        material
    )

    array = book.modifiers.new(name=f"{label} Row of 10 Books", type='ARRAY')
    array.count = 10
    array.use_relative_offset = True
    array.use_constant_offset = False
    array.relative_offset_displace = (1.14, 0.0, 0.0)
    array.use_merge_vertices = False

# Keep selection tidy
bpy.ops.object.select_all(action='DESELECT')
