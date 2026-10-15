import bpy
import bmesh
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Walls
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.5))
walls = bpy.context.active_object
walls.name = "Walls"
walls.scale = (2.0, 1.5, 1.5)

# Roof (four-sided pyramid)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=3.0, depth=2.5, location=(0, 0, 3.0))
roof = bpy.context.active_object
roof.name = "Roof"
roof.rotation_euler = (0, 0, math.pi / 4)

# Remove the closed bottom face of the cone so it's an open pyramid
bm = bmesh.new()
bm.from_mesh(roof.data)
faces_to_delete = [f for f in bm.faces if all(abs(v.co.z) < 1e-5 for v in f.verts)]
for f in faces_to_delete:
    bm.faces.remove(f)
bm.to_mesh(roof.data)
bm.free()

def create_plane(name, verts_data, location):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location

    bm = bmesh.new()
    verts = [bm.verts.new((x, y, z)) for (x, y, z) in verts_data]
    bm.faces.new(verts)
    bm.to_mesh(mesh)
    bm.free()
    return obj

front_y = 1.51

# Door
door_verts = [
    (-0.6, 0.0, 0.0),
    (-0.6, 0.0, 2.0),
    (0.6, 0.0, 2.0),
    (0.6, 0.0, 0.0),
]
door = create_plane("Door", door_verts, (0, front_y, 0))

# Window (left one, mirrored to create the right one)
win_w = 1.0
win_h = 1.0
win_x = -1.5
win_z = 1.7
xmin = win_x - win_w / 2
xmax = win_x + win_w / 2
zmin = win_z - win_h / 2
zmax = win_z + win_h / 2
window_verts = [
    (xmin, 0.0, zmin),
    (xmin, 0.0, zmax),
    (xmax, 0.0, zmax),
    (xmax, 0.0, zmin),
]
window = create_plane("Window", window_verts, (0, front_y, 0))

# Mirror modifier to add the symmetric right window
mirror = window.modifiers.new(name="WindowMirror", type='MIRROR')
mirror.axis[0] = True
mirror.use_flip_normals = True
