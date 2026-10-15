import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    if datablocks != bpy.data.materials:
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

# Materials
def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

wall_mat = make_material("Wall", (0.65, 0.38, 0.20))
roof_mat = make_material("Roof", (0.18, 0.08, 0.04))
door_mat = make_material("Door", (0.12, 0.045, 0.02))
window_mat = make_material("Glass", (0.08, 0.35, 0.55))

# Create a box mesh directly, keeping its object origin at world origin
def create_box(name, center, size, material):
    cx, cy, cz = center
    sx, sy, sz = size
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2

    verts = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5),
        (0, 4, 5, 1), (1, 5, 6, 2),
        (2, 6, 7, 3), (4, 0, 3, 7)
    ]

    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj

# Main walls
create_box("House_Walls", (0.0, 0.0, 1.5), (4.0, 3.0, 3.0), wall_mat)

# Four-sided pyramid roof
bpy.ops.mesh.primitive_cone_add(
    vertices=4,
    radius1=3.0,
    radius2=0.0,
    depth=1.8,
    end_fill_type='NGON',
    location=(0.0, 0.0, 3.9),
    rotation=(0.0, 0.0, 0.785398)
)
roof = bpy.context.object
roof.name = "Four_Sided_Roof"
roof.data.materials.append(roof_mat)

# Front door
create_box("Front_Door", (0.0, -1.56, 0.9), (0.9, 0.14, 1.8), door_mat)

# One front window, mirrored across the X axis
window = create_box("Window_Symmetric", (1.15, -1.57, 1.9), (0.85, 0.12, 0.75), window_mat)

mirror = window.modifiers.new("Symmetrical_Windows", 'MIRROR')
mirror.use_axis[0] = True
mirror.use_clip = False
mirror.use_mirror_merge = True

# Add a small rear window pair using the same symmetry concept
rear_window = create_box("Rear_Window_Symmetric", (1.15, 1.57, 1.9), (0.85, 0.12, 0.75), window_mat)

rear_mirror = rear_window.modifiers.new("Symmetrical_Rear_Windows", 'MIRROR')
rear_mirror.use_axis[0] = True
rear_mirror.use_clip = False
rear_mirror.use_mirror_merge = True

# Flat shading for the low-poly style
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for polygon in obj.data.polygons:
            polygon.use_smooth = False
