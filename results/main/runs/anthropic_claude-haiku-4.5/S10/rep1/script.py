import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new cube mesh
mesh = bpy.data.meshes.new("CubeMesh")
obj = bpy.data.objects.new("Cube", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Create cube geometry using bmesh
bm = bmesh.new()
vertices = [
    bm.verts.new((-1, -1, -1)),
    bm.verts.new((1, -1, -1)),
    bm.verts.new((1, 1, -1)),
    bm.verts.new((-1, 1, -1)),
    bm.verts.new((-1, -1, 1)),
    bm.verts.new((1, -1, 1)),
    bm.verts.new((1, 1, 1)),
    bm.verts.new((-1, 1, 1)),
]

# Create cube faces
faces = [
    bm.faces.new([vertices[0], vertices[1], vertices[2], vertices[3]]),  # bottom
    bm.faces.new([vertices[4], vertices[7], vertices[6], vertices[5]]),  # top
    bm.faces.new([vertices[0], vertices[4], vertices[5], vertices[1]]),  # front
    bm.faces.new([vertices[2], vertices[6], vertices[7], vertices[3]]),  # back
    bm.faces.new([vertices[0], vertices[3], vertices[7], vertices[4]]),  # left
    bm.faces.new([vertices[1], vertices[5], vertices[6], vertices[2]]),  # right
]

bm.to_mesh(mesh)
bm.free()
mesh.update()

# Create three materials (red, green, blue)
red_mat = bpy.data.materials.new(name="Red")
red_mat.use_nodes = True
red_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.0, 0.0, 1.0)

green_mat = bpy.data.materials.new(name="Green")
green_mat.use_nodes = True
green_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 1.0, 0.0, 1.0)

blue_mat = bpy.data.materials.new(name="Blue")
blue_mat.use_nodes = True
blue_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.0, 1.0, 1.0)

# Add materials to the object's material slots
obj.data.materials.append(red_mat)
obj.data.materials.append(green_mat)
obj.data.materials.append(blue_mat)

# Assign materials to faces using material indices
for i, face in enumerate(mesh.polygons):
    if i < 2:
        face.material_index = 0  # Red for first two faces
    elif i < 4:
        face.material_index = 1  # Green for next two faces
    else:
        face.material_index = 2  # Blue for last two faces

mesh.update()
