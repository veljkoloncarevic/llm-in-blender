import bpy

# Clear all existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create the Floor Plane
bpy.ops.mesh.primitive_plane_size(size=10.0)
plane = bpy.context.active_object
plane.name = "CheckerFloor"
plane.location = (0, 0, 0)

# Create material for the floor plane
floor_mat = bpy.data.materials.new(name="CheckerMaterial")
floor_mat.use_nodes = True
nodes = floor_mat.node_tree.nodes
links = floor_mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add Output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

# Add Principled BSDF node
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (100, 0)
# Set roughness a bit higher for a matte floor
principled_node.inputs['Roughness'].default_value = 0.3

# Add Checker Texture node
checker_node = nodes.new(type='ShaderNodeTexChecker')
checker_node.location = (-200, 0)
# Optional: scale the checker pattern for a nice density
checker_node.inputs['Scale'].default_value = 5.0

# Connect Checker Texture Color to Principled BSDF Base Color
links.new(checker_node.outputs['Color'], principled_node.inputs['Base Color'])

# Connect Principled BSDF Shader to Material Output Surface
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to the floor plane
plane.data.materials.append(floor_mat)


# 2. Create the Glossy Red Cube
bpy.ops.mesh.primitive_cube_size(size=2.0)
cube = bpy.context.active_object
cube.name = "GlossyRedCube"
# Place the cube so its bottom rests on the floor (z = 1.0)
cube.location = (0, 0, 1.0)

# Create material for the cube
cube_mat = bpy.data.materials.new(name="GlossyRedMaterial")
cube_mat.use_nodes = True
c_nodes = cube_mat.node_tree.nodes

# Clear default nodes
c_nodes.clear()

# Add Output node
c_output_node = c_nodes.new(type='ShaderNodeOutputMaterial')
c_output_node.location = (200, 0)

# Add Principled BSDF node configured for a glossy red appearance
c_principled_node = c_nodes.new(type='ShaderNodeBsdfPrincipled')
c_principled_node.location = (0, 0)
# Set vibrant red base color
c_principled_node.inputs['Base Color'].default_value = (0.8, 0.02, 0.02, 1.0)
# Set low roughness for a glossy/shiny look
c_principled_node.inputs['Roughness'].default_value = 0.1

# Link cube material
cube_mat.node_tree.links.new(c_principled_node.outputs['BSDF'], c_output_node.inputs['Surface'])

# Assign material to the cube
cube.data.materials.append(cube_mat)
