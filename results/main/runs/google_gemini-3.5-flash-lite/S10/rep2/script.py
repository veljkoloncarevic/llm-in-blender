import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new cube mesh and object
bpy.ops.mesh.primitive_cube_size(size=2.0)
cube_obj = bpy.context.active_object
cube_obj.name = "ColorCube"
mesh = cube_obj.data

# Create materials
mat_red = bpy.data.materials.new(name="RedMaterial")
mat_red.use_nodes = False
mat_red.diffuse_color = (1.0, 0.0, 0.0, 1.0)

mat_green = bpy.data.materials.new(name="GreenMaterial")
mat_green.use_nodes = False
mat_green.diffuse_color = (0.0, 1.0, 0.0, 1.0)

mat_blue = bpy.data.materials.new(name="BlueMaterial")
mat_blue.use_nodes = False
mat_blue.diffuse_color = (0.0, 0.0, 1.0, 1.0)

# Assign materials to the object's material slots
cube_obj.data.materials.append(mat_red)   # Slot 0
cube_obj.data.materials.append(mat_green) # Slot 1
cube_obj.data.materials.append(mat_blue)  # Slot 2

# Assign faces to material indices
# A standard cube has 6 faces (indices 0 to 5)
for poly in mesh.polygons:
    if poly.index in (0, 1):
        poly.material_index = 0  # Red
    elif poly.index in (2, 3):
        poly.material_index = 1  # Green
    else:
        poly.material_index = 2  # Blue

# Ensure the view displays materials correctly
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
