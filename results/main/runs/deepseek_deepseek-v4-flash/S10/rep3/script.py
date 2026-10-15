import bpy
import bmesh

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube (default size = 2)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object

# Create three materials: red, green, blue
mat_red = bpy.data.materials.new("RedMaterial")
mat_red.use_nodes = True
red_bsdf = mat_red.node_tree.nodes.get("Principled BSDF")
if red_bsdf:
    red_bsdf.inputs["Base Color"].default_value = (1, 0, 0, 1)

mat_green = bpy.data.materials.new("GreenMaterial")
mat_green.use_nodes = True
green_bsdf = mat_green.node_tree.nodes.get("Principled BSDF")
if green_bsdf:
    green_bsdf.inputs["Base Color"].default_value = (0, 1, 0, 1)

mat_blue = bpy.data.materials.new("BlueMaterial")
mat_blue.use_nodes = True
blue_bsdf = mat_blue.node_tree.nodes.get("Principled BSDF")
if blue_bsdf:
    blue_bsdf.inputs["Base Color"].default_value = (0, 0, 1, 1)

# Append materials to the cube (creates material slots)
cube.data.materials.append(mat_red)
cube.data.materials.append(mat_green)
cube.data.materials.append(mat_blue)

# Assign material indices to faces based on their normal direction
mesh = cube.data
bm = bmesh.new()
bm.from_mesh(mesh)
for face in bm.faces:
    if abs(face.normal.z) > 0.5:      # top/bottom -> red
        face.material_index = 0
    elif abs(face.normal.x) > 0.5:   # left/right -> green
        face.material_index = 1
    else:                             # front/back -> blue
        face.material_index = 2
bm.to_mesh(mesh)
bm.free()

# Ensure mesh data is up to date
mesh.update()
