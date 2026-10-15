import bpy
import bmesh
import mathutils

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)


def create_box(name, width, depth, height, location):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    x = width / 2
    y = depth / 2
    z = height / 2
    loc = mathutils.Vector(location)

    verts = [
        mathutils.Vector((-x, -y, -z)) + loc,
        mathutils.Vector((x, -y, -z)) + loc,
        mathutils.Vector((x, y, -z)) + loc,
        mathutils.Vector((-x, y, -z)) + loc,
        mathutils.Vector((-x, -y, z)) + loc,
        mathutils.Vector((x, -y, z)) + loc,
        mathutils.Vector((x, y, z)) + loc,
        mathutils.Vector((-x, y, z)) + loc,
    ]
    for v in verts:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    faces = [
        [0, 1, 2, 3],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
    ]
    for face_verts in faces:
        bm.faces.new([bm.verts[i] for i in face_verts])

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# Tabletop
tabletop = create_box("Tabletop", 2.0, 1.0, 0.1, (0, 0, 0.85))

# Bevel modifier on tabletop
bevel = tabletop.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.02
bevel.segments = 1
bevel.limit_method = 'NONE'

# Four legs
leg_positions = [
    (0.9, 0.4),
    (-0.9, 0.4),
    (0.9, -0.4),
    (-0.9, -0.4),
]
for i, (x, y) in enumerate(leg_positions, start=1):
    create_box(f"Leg{i}", 0.1, 0.1, 0.8, (x, y, 0.4))
