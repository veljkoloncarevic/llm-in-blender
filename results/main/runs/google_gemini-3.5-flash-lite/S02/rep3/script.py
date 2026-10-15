import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create floor plane
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "CheckerFloor"

# Create red cube sitting on the floor
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
cube = bpy.context.active_object
cube.name = "GlossyCube"

# --- Material for Floor: Checker Texture driving Base Color ---
floor_mat = bpy.data.materials.new(name="FloorMaterial")
floor_mat.use_nodes = True
floor_nodes = floor_mat.node_tree.nodes
floor_links = floor_mat.node_tree.links

# Clear default nodes
floor_nodes.clear()

# Create nodes
node_output = floor_nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = (400, 0)

node_principled = floor_nodes.new(type='ShaderNodeBsdfPrincipled')
node_principled.location = (100, 0)

node_checker = floor_nodes.new(type='ShaderNodeTexChecker')
node_checker.location = (-200, 0)
node_checker.inputs['Scale'].default_value = 5.0

# Link Checker Color to Principled Base Color, and Principled BSDF to Output
floor_links.new(node_checker.outputs['Color'], node_principled.inputs['Base Color'])
floor_links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

# Assign material to floor
floor.data.materials.append(floor_mat)


# --- Material for Cube: Glossy Red ---
cube_mat = bpy.data.materials.new(name="GlossyRedMaterial")
cube_mat.use_nodes = True
cube_nodes = cube_mat.node_tree.nodes
cube_links = cube_mat.node_tree.links

# Clear default nodes
cube_nodes.clear()

# Create nodes
cube_output = cube_nodes.new(type='ShaderNodeOutputMaterial')
cube_output.location = (300, 0)

cube_principled = cube_nodes.new(type='ShaderNodeBsdfPrincipled')
cube_principled.location = (0, 0)

# Set properties for glossy red
cube_principled.inputs['Base Color'].default_value = (0.8, 0.05, 0.05, 1.0)
cube_principled.inputs['Roughness'].default_value = 0.1  # Make it glossy/shiny

# Link Principled BSDF to Output
cube_links.new(cube_principled.outputs['BSDF'], cube_output.inputs['Surface'])

# Assign material to cube
cube.data.materials.append(cube_mat)
