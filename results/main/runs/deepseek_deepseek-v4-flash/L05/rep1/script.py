import bpy


def clear_scene():
    """Remove all existing objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def add_box(name, dims, loc):
    """Add a cube of given dimensions (x,y,z) at loc, with scale applied to mesh."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.scale = dims
    obj.location = loc
    bpy.ops.object.transform_apply(scale=True)
    return obj


def add_book_row(name, shelf_z, book_count, thickness, depth, height, gap, shelf_thickness):
    """Create a row of book boxes using an Array modifier."""
    offset = thickness + gap
    start_x = -((book_count - 1) * offset) / 2.0

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.scale = (thickness, depth, height)
    bpy.ops.object.transform_apply(scale=True)

    array_mod = obj.modifiers.new(name="BookArray", type='ARRAY')
    array_mod.count = book_count
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace[0] = offset

    obj.location = (start_x, 0.0, shelf_z + shelf_thickness / 2.0 + height / 2.0)
    return obj


# Scene reset
clear_scene()

# Bookshelf dimensions
W = 2.0      # outer width
H = 3.0      # outer height
D = 0.5      # depth
T = 0.1      # board thickness

# Frame panels
add_box("LeftPanel", (T, D, H), (-(W / 2 - T / 2), 0.0, H / 2))
add_box("RightPanel", (T, D, H), (W / 2 - T / 2, 0.0, H / 2))
add_box("TopPanel", (W, D, T), (0.0, 0.0, H - T / 2))
add_box("BottomPanel", (W, D, T), (0.0, 0.0, T / 2))

# Three shelves
inner_width = W - 2 * T
shelf_heights = [0.8, 1.6, 2.4]
for i, z in enumerate(shelf_heights):
    add_box(f"Shelf{i + 1}", (inner_width, D, T), (0.0, 0.0, z))

# Books on each shelf
book_count = 12
book_thickness = 0.06
book_depth = 0.35
book_height = 0.4
book_gap = 0.02

for i, z in enumerate(shelf_heights):
    add_book_row(
        name=f"BookRow_{i + 1}",
        shelf_z=z,
        book_count=book_count,
        thickness=book_thickness,
        depth=book_depth,
        height=book_height,
        gap=book_gap,
        shelf_thickness=T,
    )
