import bpy


def remove_all_objects():
    """Delete all existing objects in the scene."""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_cuboid_mesh(name, dx, dy, dz):
    """Create and return a cuboid mesh with given dimensions (centered at origin)."""
    x, y, z = dx / 2.0, dy / 2.0, dz / 2.0
    verts = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y,  z), (x, -y,  z), (x, y,  z), (-x, y,  z),
    ]
    faces = [
        (0, 1, 2, 3),  # bottom
        (4, 5, 6, 7),  # top
        (0, 1, 5, 4),  # side -Y
        (1, 2, 6, 5),  # side +X
        (2, 3, 7, 6),  # side +Y
        (3, 0, 4, 7),  # side -X
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def create_object(mesh, name, location):
    """Create a new object linked to the scene collection."""
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_wood_material():
    """Create and return a simple brown wood material."""
    mat = bpy.data.materials.new("Wood")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1.0)
    return mat


def main():
    remove_all_objects()

    # Fence parameters
    post_width, post_depth = 0.1, 0.1
    post_height = 1.8
    spacing = 2.0
    post_count = 8

    rail_y, rail_z = 0.08, 0.15
    bottom_rail_z = 0.4
    top_rail_z = 1.2

    # Create a single post with an Array modifier
    post_mesh = create_cuboid_mesh("PostMesh", post_width, post_depth, post_height)
    post_obj = create_object(post_mesh, "Post", (0.0, 0.0, post_height / 2.0))

    array_mod = post_obj.modifiers.new("PostArray", 'ARRAY')
    array_mod.count = post_count
    array_mod.use_relative_offset = False
    array_mod.use_constant_offset = True
    array_mod.constant_offset_displace = (spacing, 0.0, 0.0)

    # Rails span from inner face of first post to inner face of last post
    total_span = (post_count - 1) * spacing
    rail_length = total_span - post_width
    rail_center_x = total_span / 2.0

    rail_bottom_mesh = create_cuboid_mesh("RailBottomMesh", rail_length, rail_y, rail_z)
    rail_bottom_obj = create_object(rail_bottom_mesh, "Rail_Bottom", (rail_center_x, 0.0, bottom_rail_z))

    rail_top_mesh = create_cuboid_mesh("RailTopMesh", rail_length, rail_y, rail_z)
    rail_top_obj = create_object(rail_top_mesh, "Rail_Top", (rail_center_x, 0.0, top_rail_z))

    # Apply wood material to all meshes
    wood_mat = create_wood_material()
    for mesh in (post_mesh, rail_bottom_mesh, rail_top_mesh):
        mesh.materials.append(wood_mat)


if __name__ == "__main__":
    main()
