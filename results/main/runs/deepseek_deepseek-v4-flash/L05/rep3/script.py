import bpy
import bmesh


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def create_cube_mesh(name, dims):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dims[0] / 2.0
        v.co.y *= dims[1] / 2.0
        v.co.z *= dims[2] / 2.0
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def add_cube_object(name, center, dims):
    mesh = create_cube_mesh(name + "_Mesh", dims)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = center
    return obj


def main():
    clear_scene()

    # Dimensions
    W = 8.0
    D = 2.0
    H = 6.0
    t = 0.15

    # Frame
    add_cube_object("Frame_Bottom", (W / 2, 0.0, t / 2), (W, D, t))
    add_cube_object("Frame_Top", (W / 2, 0.0, H - t / 2), (W, D, t))
    add_cube_object("Frame_Left", (t / 2, 0.0, H / 2), (t, D, H))
    add_cube_object("Frame_Right", (W - t / 2, 0.0, H / 2), (t, D, H))
    add_cube_object("Frame_Back", (W / 2, -D / 2 + t / 2, H / 2), (W, t, H))

    # Shelves
    z_bottom = t
    z_top = H - t
    inner_h = z_top - z_bottom
    shelf_dims = (W - 2 * t, D - t, t)

    shelf_top_zs = []
    for i in range(3):
        fraction = (i + 1) / 4.0
        shelf_top_z = z_bottom + fraction * inner_h
        shelf_top_zs.append(shelf_top_z)
        center_z = shelf_top_z - t / 2
        add_cube_object(f"Shelf_{i + 1}", (W / 2, t / 2, center_z), shelf_dims)

    # Books
    book_w = 0.5
    book_d = 1.5
    book_h = 1.2
    book_mesh = create_cube_mesh("BookMesh", (book_w, book_d, book_h))

    count = 12
    total_row_width = book_w * count
    start_x = (W - total_row_width) / 2.0
    row_center_x = start_x + book_w / 2.0

    for i in range(3):
        object_name = f"BookRow_{i + 1}"
        obj = bpy.data.objects.new(object_name, book_mesh)
        bpy.context.scene.collection.objects.link(obj)

        book_z = shelf_top_zs[i] + book_h / 2.0
        obj.location = (row_center_x, t / 2, book_z)

        mod = obj.modifiers.new("Array", 'ARRAY')
        mod.count = count
        mod.relative_offset_displace = (1.0, 0.0, 0.0)


main()
