import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube mesh
cube_data = bpy.data.meshes.new("CubeMesh")
cube_obj = bpy.data.objects.new("Cube", cube_data)
bpy.context.collection.objects.link(cube_obj)
bpy.context.view_layer.objects.active = cube_obj
cube_obj.select_set(True)

# Create cube geometry using bmesh
bm = bmesh.new()
verts = [
    bm.verts.new((-1, -1, -1)),
    bm.verts.new((1, -1, -1)),
    bm.verts.new((1, 1, -1)),
    bm.verts.new((-1, 1, -1)),
    bm.verts.new((-1, -1, 1)),
    bm.verts.new((1, -1, 1)),
    bm.verts.new((1, 1, 1)),
    bm.verts.new((-1, 1, 1)),
]

# Create faces
faces = [
    bm.faces.new([verts[0], verts[1], verts[2], verts[3]]),  # Bottom
    bm.faces.new([verts[4], verts[7], verts[6], verts[5]]),  # Top
    bm.faces.new([verts[0], verts[4], verts[5], verts[1]]),  # Front
    bm.faces.new([verts[2], verts[6], verts[7], verts[3]]),  # Back
    bm.faces.new([verts[0], verts[3], verts[7], verts[4]]),  # Left
    bm.faces.new([verts[1], verts[5], verts[6], verts[2]]),  # Right
]

bm.to_mesh(cube_data)
bm.free()

# Create three materials: Red, Green, Blue
red_mat = bpy.data.materials.new(name="Red")
red_mat.use_nodes = True
red_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.0, 0.0, 1.0)

green_mat = bpy.data.materials.new(name="Green")
green_mat.use_nodes = True
green_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 1.0, 0.0, 1.0)

blue_mat = bpy.data.materials.new(name="Blue")
blue_mat.use_nodes = True
blue_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.0, 1.0, 1.0)

# Add materials to material slots
cube_obj.data.materials.append(red_mat)
cube_obj.data.materials.append(green_mat)
cube_obj.data.materials.append(blue_mat)

# Assign materials to faces using face material indices
for i, face in enumerate(cube_data.polygons):
    if i == 0 or i == 1:
        face.material_index = 0  # Red for bottom and top
    elif i == 2 or i == 3:
        face.material_index = 1  # Green for front and back
    else:
        face.material_index = 2  # Blue for left and right

# Update the mesh
cube_data.update()
