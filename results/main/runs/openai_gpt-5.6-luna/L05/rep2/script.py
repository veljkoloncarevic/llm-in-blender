import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

frame_mat = make_material("Warm Wood", (0.30, 0.12, 0.045))
book_mats = [
    make_material("Book Red", (0.55, 0.06, 0.04)),
    make_material("Book Blue", (0.04, 0.18, 0.50)),
    make_material("Book Green", (0.06, 0.35, 0.12)),
]

def create_cube(name, location, dimensions, material):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj

# Overall bookshelf dimensions:
# width: 6.0, depth: 0.65, height: 7.0
# Vertical side panels
create_cube("Left Side", (-2.85, 0.0, 0.0), (0.30, 0.65, 7.0), frame_mat)
create_cube("Right Side", (2.85, 0.0, 0.0), (0.30, 0.65, 7.0), frame_mat)

# Bottom, three shelves, and top
horizontal_levels = [-3.35, -1.10, 1.15, 3.40]
for index, z in enumerate(horizontal_levels):
    label = "Bottom" if index == 0 else ("Top" if index == 4 else f"Shelf {index}")
    create_cube(label, (0.0, 0.0, z), (5.70, 0.65, 0.30), frame_mat)

# Create one book per shelf level, then use an Array modifier for ten books per row
book_rows = [
    (-2.40, book_mats[0]),
    (-0.15, book_mats[1]),
    (2.10, book_mats[2]),
]

for row_index, (z, material) in enumerate(book_rows, start=1):
    book = create_cube(
        f"Row {row_index} Book",
        (-2.42, -0.03, z),
        (0.40, 0.48, 1.75),
        material
    )

    array = book.modifiers.new(name="Ten Books Array", type='ARRAY')
    array.count = 10
    array.use_relative_offset = False
    array.use_constant_offset = True
    array.constant_offset_displace = (0.48, 0.0, 0.0)

# Set a clean object selection state
bpy.ops.object.select_all(action='DESELECT')
