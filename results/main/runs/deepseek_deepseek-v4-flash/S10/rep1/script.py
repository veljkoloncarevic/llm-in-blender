import bpy
import bmesh

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create a new cube mesh and object
mesh = bpy.data.meshes.new("Cube")
obj = bpy.data.objects.new("Cube", mesh)
bpy.context.collection.objects.link(obj)

# Build cube geometry with bmesh
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2)
bm.to_mesh(mesh)
bm.free()

# Create three coloured materials
mat_red = bpy.data.materials.new("Red")
mat_green = bpy.data.materials.new("Green")
mat_blue = bpy.data.materials.new("Blue")

def set_material_color(mat, color):
    """Set both viewport and renderable base colour."""
    if mat.node_tree is None:
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
    mat.diffuse_color = color

set_material_color(mat_red, (1.0, 0.0, 0.0, 1.0))
set_material_color(mat_green, (0.0, 1.0, 0.0, 1.0))
set_material_color(mat_blue, (0.0, 0.0, 1.0, 1.0))

# Assign the three materials as slots on the mesh
mesh.materials.append(mat_red)
mesh.materials.append(mat_green)
mesh.materials.append(mat_blue)

# Assign material indices to the six cube faces:
# faces 0&1 -> red, 2&3 -> green, 4&5 -> blue
for i, poly in enumerate(mesh.polygons):
    poly.material_index = i // 2

# Make the new cube the active object
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
