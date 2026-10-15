import bpy
import bmesh

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Fence parameters
fence_length = 5.0
num_posts = 8
spacing = fence_length / (num_posts - 1)

post_width = 0.1
post_shoulder_height = 1.3
post_height = 1.5

rail_length = fence_length
rail_width = 0.04
rail_height = 0.12
top_rail_z = 1.1
bottom_rail_z = 0.5


def create_mesh_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# Build the post mesh (square post with a pyramidal cap)
bm = bmesh.new()
verts = [
    (-post_width / 2, -post_width / 2, 0.0),
    (post_width / 2, -post_width / 2, 0.0),
    (post_width / 2, post_width / 2, 0.0),
    (-post_width / 2, post_width / 2, 0.0),
    (-post_width / 2, -post_width / 2, post_shoulder_height),
    (post_width / 2, -post_width / 2, post_shoulder_height),
    (post_width / 2, post_width / 2, post_shoulder_height),
    (-post_width / 2, post_width / 2, post_shoulder_height),
    (0.0, 0.0, post_height),
]
for v in verts:
    bm.verts.new(v)
bm.verts.ensure_lookup_table()

faces = [
    (0, 1, 5, 4),  # side
    (1, 2, 6, 5),  # side
    (2, 3, 7, 6),  # side
    (3, 0, 4, 7),  # side
    (4, 5, 8),     # cap
    (5, 6, 8),     # cap
    (6, 7, 8),     # cap
    (7, 4, 8),     # cap
    (0, 3, 2, 1),  # bottom
]
for face in faces:
    bm.faces.new([bm.verts[i] for i in face])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

post_obj = create_mesh_object("FencePost", bm)
post_obj.location = (0.0, 0.0, 0.0)

# Add array modifier to duplicate the post
array_mod = post_obj.modifiers.new(name="Array", type='ARRAY')
array_mod.count = num_posts
array_mod.use_relative_offset = False
array_mod.use_constant_offset = True
array_mod.constant_offset_displace = (spacing, 0.0, 0.0)


def create_rail(name, center_z):
    bm = bmesh.new()
    x = rail_length / 2.0
    y = rail_width / 2.0
    z = rail_height / 2.0
    verts = [
        (-x, -y, -z),
        (x, -y, -z),
        (x, y, -z),
        (-x, y, -z),
        (-x, -y, z),
        (x, -y, z),
        (x, y, z),
        (-x, y, z),
    ]
    for v in verts:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    faces = [
        (0, 3, 2, 1),  # bottom
        (4, 5, 6, 7),  # top
        (0, 1, 5, 4),  # front
        (1, 2, 6, 5),  # right
        (2, 3, 7, 6),  # back
        (3, 0, 4, 7),  # left
    ]
    for face in faces:
        bm.faces.new([bm.verts[i] for i in face])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    rail_obj = create_mesh_object(name, bm)
    rail_obj.location = (rail_length / 2.0, 0.0, center_z)
    return rail_obj


create_rail("TopRail", top_rail_z)
create_rail("BottomRail", bottom_rail_z)
