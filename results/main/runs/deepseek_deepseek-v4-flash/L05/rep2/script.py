import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


def create_cuboid_mesh(name, width, depth, height):
    """Create a mesh data block containing a centered cuboid."""
    mesh = bpy.data.meshes.new(name)
    hx, hy, hz = width / 2.0, depth / 2.0, height / 2.0

    verts = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)
    ]
    faces = [
        (0, 3, 2, 1),  # bottom
        (4, 5, 6, 7),  # top
        (0, 1, 5, 4),  # front (-Y)
        (3, 7, 6, 2),  # back (+Y)
        (0, 4, 7, 3),  # left (-X)
        (1, 2, 6, 5),  # right (+X)
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def add_cuboid(name, width, depth, height, location):
    mesh = create_cuboid_mesh(name, width, depth, height)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    return obj


# Bookshelf dimensions
W = 2.0
D = 0.5
H = 3.0
t = 0.1

# Frame
add_cuboid("Shelf_Left", t, D, H, (t / 2, D / 2, H / 2))
add_cuboid("Shelf_Right", t, D, H, (W - t / 2, D / 2, H / 2))
add_cuboid("Shelf_Bottom", W, D, t, (W / 2, D / 2, t / 2))
add_cuboid("Shelf_Top", W, D, t, (W / 2, D / 2, H - t / 2))
add_cuboid("Shelf_Back", W, t, H, (W / 2, D - t / 2, H / 2))

# Three horizontal shelves
shelf_heights = [0.6, 1.4, 2.2]
shelf_width = W - 2 * t
shelf_depth = D - t
shelf_center_x = W / 2
shelf_center_y = (D - t) / 2

for i, z_shelf in enumerate(shelf_heights):
    add_cuboid(
        f"Shelf_Level_{i + 1}",
        shelf_width,
        shelf_depth,
        t,
        (shelf_center_x, shelf_center_y, z_shelf - t / 2)
    )

# Book dimensions
book_thickness = 0.05
book_depth = 0.3
book_height = 0.6
gap = 0.02
count = 12

book_mesh = create_cuboid_mesh("Book", book_thickness, book_depth, book_height)

# Row placement calculations
row_length = count * book_thickness + (count - 1) * gap
x_start = t + (shelf_width - row_length) / 2
x_first_center = x_start + book_thickness / 2
y_book = (D - t) - book_depth / 2
offset_x = book_thickness + gap

for i, z_shelf in enumerate(shelf_heights):
    obj = bpy.data.objects.new(f"Book_Row_{i + 1}", book_mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = (x_first_center, y_book, z_shelf + book_height / 2)

    arr = obj.modifiers.new(name="Array", type='ARRAY')
    arr.count = count
    arr.use_relative_offset = False
    arr.use_constant_offset = True
    arr.constant_offset_displace[0] = offset_x
