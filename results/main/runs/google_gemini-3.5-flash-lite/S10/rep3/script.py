import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new cube mesh and object
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
cube_obj = bpy.active_object
cube_obj.name = "ColoredCube"
mesh = cube_obj.data

# Create materials
mat_red = bpy.data.materials.new(name="RedMaterial")
mat_red.use_nodes = True
mat_red.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)

mat_green = bpy.data.materials.new(name="GreenMaterial")
mat_green.use_nodes = True
mat_green.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 1.0)

mat_blue = bpy.data.materials.new(name="BlueMaterial")
mat_blue.use_nodes = True
mat_blue.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)

# Assign materials to the object's material slots
cube_obj.data.materials.append(mat_red)   # Slot 0
cube_obj.data.materials.append(mat_green) # Slot 1
cube_obj.data.materials.append(mat_blue)  # Slot 2

# Assign material indices to the faces
# A cube has 6 faces (0 to 5)
# We map them to the 3 different material slots (0, 1, 2)
for face in mesh.polygons:
    if face.index in (0, 1):
        face.material_index = 0  # Red
    elif face.index in (2, 3):
        face.material_index = 1  # Green
    else:
        face.material_index = 2  # Blue
