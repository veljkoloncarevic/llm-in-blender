import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create materials
def create_material(name, color):
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (*color, 1.0)
    return material

red_material = create_material("Red", (1.0, 0.0, 0.0))
green_material = create_material("Green", (0.0, 1.0, 0.0))
blue_material = create_material("Blue", (0.0, 0.0, 1.0))

# Cube vertices and faces
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
    (0, 3, 2, 1),  # Bottom
    (4, 5, 6, 7),  # Top
    (0, 1, 5, 4),  # Front
    (1, 2, 6, 5),  # Right
    (2, 3, 7, 6),  # Back
    (3, 0, 4, 7),  # Left
]

mesh = bpy.data.meshes.new("ThreeColorCubeMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

cube = bpy.data.objects.new("ThreeColorCube", mesh)
bpy.context.collection.objects.link(cube)

# Add material slots
cube.data.materials.append(red_material)
cube.data.materials.append(green_material)
cube.data.materials.append(blue_material)

# Assign material indices: two faces per color
material_indices = [0, 0, 1, 1, 2, 2]
for polygon, material_index in zip(mesh.polygons, material_indices):
    polygon.material_index = material_index
