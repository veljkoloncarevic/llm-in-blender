import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

def create_box(name, center, size):
    cx, cy, cz = center
    sx, sy, sz = size
    hx, hy, hz = sx / 2, sy / 2, sz / 2

    verts = [
        (cx - hx, cy - hy, cz - hz),
        (cx + hx, cy - hy, cz - hz),
        (cx + hx, cy + hy, cz - hz),
        (cx - hx, cy + hy, cz - hz),
        (cx - hx, cy - hy, cz + hz),
        (cx + hx, cy - hy, cz + hz),
        (cx + hx, cy + hy, cz + hz),
        (cx - hx, cy + hy, cz + hz),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# Tabletop
tabletop = create_box("Tabletop", (0.0, 0.0, 0.725), (1.2, 0.8, 0.05))

# Four legs
leg_positions = [
    (-0.575, -0.375),
    (0.575, -0.375),
    (0.575, 0.375),
    (-0.575, 0.375),
]
for i, (x, y) in enumerate(leg_positions, start=1):
    create_box(f"Leg_{i}", (x, y, 0.35), (0.05, 0.05, 0.7))

# Add Bevel modifier to the tabletop
bevel_mod = tabletop.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.02
bevel_mod.segments = 1
