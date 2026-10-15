import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
mesh = cube.data

# Create three materials: red, green, and blue
materials = {}
colors = {
    'Red': (1.0, 0.0, 0.0, 1.0),
    'Green': (0.0, 1.0, 0.0, 1.0),
    'Blue': (0.0, 0.0, 1.0, 1.0)
}

for name, color in colors.items():
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
    materials[name] = mat
    mesh.materials.append(mat)

# Assign materials to faces using bmesh
bm = bmesh.new()
bm.from_mesh(mesh)
bm.faces.ensure_lookup_table()

# Assign red material to first two faces
for i in range(2):
    bm.faces[i].material_index = 0

# Assign green material to next two faces
for i in range(2, 4):
    bm.faces[i].material_index = 1

# Assign blue material to last two faces
for i in range(4, 6):
    bm.faces[i].material_index = 2

bm.to_mesh(mesh)
bm.free()

# Update the mesh
mesh.update()

# Set the object to solid shading mode to see materials
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'
                space.shading.use_scene_lights = True
