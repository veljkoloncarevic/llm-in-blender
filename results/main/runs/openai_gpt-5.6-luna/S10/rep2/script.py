import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube mesh
vertices = [
    (-1, -1, -1),
    ( 1, -1, -1),
    ( 1,  1, -1),
    (-1,  1, -1),
    (-1, -1,  1),
    ( 1, -1,  1),
    ( 1,  1,  1),
    (-1,  1,  1),
]

faces = [
    (0, 1, 2, 3),  # Bottom
    (4, 7, 6, 5),  # Top
    (0, 4, 5, 1),  # Front
    (1, 5, 6, 2),  # Right
    (2, 6, 7, 3),  # Back
    (4, 0, 3, 7),  # Left
]

mesh = bpy.data.meshes.new("ThreeColorCubeMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

cube = bpy.data.objects.new("ThreeColorCube", mesh)
bpy.context.collection.objects.link(cube)

# Create materials
red_material = bpy.data.materials.new("Red")
red_material.diffuse_color = (1.0, 0.0, 0.0, 1.0)

green_material = bpy.data.materials.new("Green")
green_material.diffuse_color = (0.0, 1.0, 0.0, 1.0)

blue_material = bpy.data.materials.new("Blue")
blue_material.diffuse_color = (0.0, 0.0, 1.0, 1.0)

# Add materials as mesh slots
cube.data.materials.append(red_material)
cube.data.materials.append(green_material)
cube.data.materials.append(blue_material)

# Assign material indices to different faces
# Bottom and top: red
# Front and back: green
# Right and left: blue
material_indices = [0, 0, 1, 2, 1, 2]

for polygon, material_index in zip(cube.data.polygons, material_indices):
    polygon.material_index = material_index

# Make the cube the active selected object
bpy.context.view_layer.objects.active = cube
cube.select_set(True)
