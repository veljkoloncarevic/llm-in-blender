import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Helpers
def make_cube(name, location, dimensions, color):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    mat = bpy.data.materials.new(name + "_Material")
    mat.diffuse_color = (*color, 1.0)
    obj.data.materials.append(mat)
    return obj

# Materials/colors
frame_color = (0.22, 0.09, 0.035)
shelf_color = (0.30, 0.13, 0.05)
back_color = (0.14, 0.055, 0.02)
book_colors = [
    (0.65, 0.08, 0.05),
    (0.05, 0.22, 0.55),
    (0.78, 0.48, 0.06),
]

# Overall bookshelf dimensions
width = 6.0
height = 7.0
depth = 1.4
side_thickness = 0.25
panel_thickness = 0.25

# Box frame
make_cube(
    "Left_Side",
    (-(width - side_thickness) / 2, 0, 0),
    (side_thickness, depth, height),
    frame_color
)
make_cube(
    "Right_Side",
    ((width - side_thickness) / 2, 0, 0),
    (side_thickness, depth, height),
    frame_color
)
make_cube(
    "Top",
    (0, 0, (height - panel_thickness) / 2),
    (width - 2 * side_thickness, depth, panel_thickness),
    frame_color
)
make_cube(
    "Bottom",
    (0, 0, -(height - panel_thickness) / 2),
    (width - 2 * side_thickness, depth, panel_thickness),
    frame_color
)

# Thin rear panel
make_cube(
    "Back_Panel",
    (0, depth / 2 - 0.08, 0),
    (width - 2 * side_thickness, 0.16, height - 2 * panel_thickness),
    back_color
)

# Three horizontal shelves
shelf_z_positions = (-1.45, 0.75, 2.95)
for index, z in enumerate(shelf_z_positions, start=1):
    make_cube(
        f"Shelf_{index}",
        (0, 0, z),
        (width - 2 * side_thickness, depth, 0.20),
        shelf_color
    )

# Books: one source cube and Array modifier per shelf, ten books per row
book_width = 0.31
book_depth = 1.02
book_heights = (1.55, 1.65, 1.40)
book_start_x = -2.42
book_y = -0.08

for row, shelf_z in enumerate(shelf_z_positions):
    book_height = book_heights[row]
    book = make_cube(
        f"Bookshelf_Row_{row + 1}",
        (
            book_start_x,
            book_y,
            shelf_z + 0.10 + book_height / 2
        ),
        (book_width, book_depth, book_height),
        book_colors[row]
    )

    array = book.modifiers.new(name="Ten_Book_Array", type='ARRAY')
    array.count = 10
    array.use_relative_offset = True
    array.use_constant_offset = False
    array.relative_offset_displace = (1.28, 0.0, 0.0)

# Keep a clean object selection state
bpy.ops.object.select_all(action='DESELECT')
