import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new mesh and object for the cube
mesh = bpy.data.meshes.new(name="ColoredCubeMesh")
cube_obj = bpy.data.objects.new(name="ColoredCube", object_data=mesh)

# Link the object to the active collection
bpy.context.collection.objects.link(cube_obj)

# Create 3 distinct materials: Red, Green, Blue
mat_red = bpy.data.materials.new(name="RedMaterial")
mat_red.use_nodes = True
mat_red.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)

mat_green = bpy.data.materials.new(name="GreenMaterial")
mat_green.use_nodes = True
mat_green.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 1.0)

mat_blue = bpy.data.materials.new(name="BlueMaterial")
mat_blue.use_nodes = True
mat_blue.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)

# Add materials to the object's material slots (Indices: 0=Red, 1=Green, 2=Blue)
cube_obj.data.materials.append(mat_red)
cube_obj.data.materials.append(mat_green)
cube_obj.data.materials.append(mat_blue)

# Define geometry data for a primitive cube
vertices = [
    (-1.0, -1.0, -1.0),
    ( 1.0, -1.0, -1.0),
    ( 1.0,  1.0, -1.0),
    (-1.0,  1.0, -1.0),
    (-1.0, -1.0,  1.0),
    ( 1.0, -1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    (-1.0,  1.0,  1.0)
]

faces = [
    (0, 1, 2, 3), # Bottom
    (4, 7, 6, 5), # Top
    (0, 4, 5, 1), # Front
    (1, 5, 6, 2), # Right
    (2, 6, 7, 3), # Back
    (3, 7, 4, 0)  # Left
]

# Build the mesh from vertices and faces
mesh.from_pydata(vertices, [], faces)
mesh.update()

# Assign material indices to individual faces
# We will cycle through the 3 materials (0, 1, 2) across the 6 faces
for face_index, poly in enumerate(mesh.polygons):
    poly.material_index = face_index % 3

# Set the active object to our cube and make it active in the viewport
bpy.context.view_layer.objects.active = cube_obj
cube_obj.select_set(True)
