import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create floor plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Create cube sitting on the floor
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "Cube"

# --- Floor material: black-and-white checker ---
floor_mat = bpy.data.materials.new(name="FloorMaterial")
floor_mat.use_nodes = True
mat_nodes = floor_mat.node_tree.nodes
mat_links = floor_mat.node_tree.links
mat_nodes.clear()

principled = mat_nodes.new(type='ShaderNodeBsdfPrincipled')
output = mat_nodes.new(type='ShaderNodeOutputMaterial')
tex_coord = mat_nodes.new(type='ShaderNodeTexCoord')
checker = mat_nodes.new(type='ShaderNodeTexChecker')

# Ensure black-and-white checker
checker.inputs["Color1"].default_value = (0, 0, 0, 1)
checker.inputs["Color2"].default_value = (1, 1, 1, 1)

mat_links.new(tex_coord.outputs["Generated"], checker.inputs["Vector"])
mat_links.new(checker.outputs["Color"], principled.inputs["Base Color"])
mat_links.new(principled.outputs["BSDF"], output.inputs["Surface"])

floor.data.materials.append(floor_mat)

# --- Cube material: glossy red ---
cube_mat = bpy.data.materials.new(name="CubeMaterial")
cube_mat.use_nodes = True
cube_nodes = cube_mat.node_tree.nodes
cube_links = cube_mat.node_tree.links
cube_nodes.clear()

cube_principled = cube_nodes.new(type='ShaderNodeBsdfPrincipled')
cube_output = cube_nodes.new(type='ShaderNodeOutputMaterial')

cube_principled.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)
cube_principled.inputs["Roughness"].default_value = 0.2

cube_links.new(cube_principled.outputs["BSDF"], cube_output.inputs["Surface"])

cube.data.materials.append(cube_mat)

# Set active object (optional)
bpy.context.view_layer.objects.active = cube
