import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    return mat

wall_mat = make_material("Warm Wall", (0.72, 0.42, 0.22))
roof_mat = make_material("Roof", (0.18, 0.08, 0.04))
door_mat = make_material("Door", (0.20, 0.07, 0.025))
window_mat = make_material("Window", (0.08, 0.35, 0.55))

def add_cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    return obj

# Main house walls
walls = add_cube(
    "Walls",
    (0.0, 0.0, 1.5),
    (4.0, 4.0, 3.0),
    wall_mat
)

# Four-sided pyramid roof
bpy.ops.mesh.primitive_cone_add(
    vertices=4,
    radius1=3.05,
    radius2=0.0,
    depth=2.0,
    end_fill_type='NGON',
    location=(0.0, 0.0, 4.0),
    rotation=(0.0, 0.0, math.radians(45.0))
)
roof = bpy.context.object
roof.name = "Four-Sided Pyramid Roof"
roof.data.materials.append(roof_mat)

# Front door
door = add_cube(
    "Door",
    (0.0, -2.06, 0.9),
    (0.9, 0.14, 1.8),
    door_mat
)

# Build one front window mesh on the positive X side.
# Its geometry is mirrored across the global X=0 plane.
verts = [
    (0.65, -2.08, 1.35), (1.45, -2.08, 1.35),
    (1.45, -2.08, 2.15), (0.65, -2.08, 2.15),
    (0.65, -2.20, 1.35), (1.45, -2.20, 1.35),
    (1.45, -2.20, 2.15), (0.65, -2.20, 2.15),
]
faces = [
    (0, 1, 2, 3),
    (4, 7, 6, 5),
    (0, 4, 5, 1),
    (1, 5, 6, 2),
    (2, 6, 7, 3),
    (4, 0, 3, 7),
]

mesh = bpy.data.meshes.new("WindowMesh")
mesh.from_pydata(verts, [], faces)
mesh.update()

window = bpy.data.objects.new("Symmetrical Windows", mesh)
bpy.context.collection.objects.link(window)
window.data.materials.append(window_mat)

mirror = window.modifiers.new("Mirror Windows", 'MIRROR')
mirror.use_axis[0] = True
mirror.use_clip = True
mirror.use_mirror_merge = True
mirror.merge_threshold = 0.001

# Add simple roof-facing side orientation while keeping the low-poly design clean
for obj in (walls, roof, door, window):
    obj.select_set(False)

# Set the walls as the active object for a predictable scene state
walls.select_set(True)
bpy.context.view_layer.objects.active = walls
