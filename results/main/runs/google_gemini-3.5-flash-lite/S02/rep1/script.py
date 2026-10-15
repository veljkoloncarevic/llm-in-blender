import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create Floor Plane
bpy.ops.mesh.primitive_plane_size = 10.0
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Create Material for Floor
floor_mat = bpy.data.materials.new(name="CheckerFloorMat")
floor_mat.use_nodes = True
floor.data.materials.append(floor_mat)

# Setup Procedural Checker Texture on Floor
nodes = floor_mat.node_tree.nodes
links = floor_mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add Output and Principled BSDF
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

principled_floor = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_floor.location = (100, 0)
principled_floor.inputs['Roughness'].default_value = 0.3

# Add Checker Texture and Texture Coordinate
checker_node = nodes.new(type='ShaderNodeTexChecker')
checker_node.location = (-300, 0)
checker_node.inputs['Scale'].default_value = 5.0
checker_node.inputs['Color1'].default_value = (0.05, 0.05, 0.05, 1.0) # Dark gray/black
checker_node.inputs['Color2'].default_value = (0.9, 0.9, 0.9, 1.0)     # White

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-500, 0)

# Link nodes
links.new(tex_coord.outputs['Generated'], checker_node.inputs['Vector'])
links.new(checker_node.outputs['Color'], principled_floor.inputs['Base Color'])
links.new(principled_floor.outputs['BSDF'], output_node.inputs['Surface'])


# 2. Create Glossy Red Cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
cube = bpy.context.active_object
cube.name = "GlossyCube"

# Create Material for Cube
cube_mat = bpy.data.materials.new(name="GlossyRedMat")
cube_mat.use_nodes = True
cube.data.materials.append(cube_mat)

# Setup Glossy Red Material using Principled BSDF
cube_nodes = cube_mat.node_tree.nodes
cube_links = cube_mat.node_tree.links

cube_nodes.clear()

cube_output = cube_nodes.new(type='ShaderNodeOutputMaterial')
cube_output.location = (300, 0)

principled_cube = cube_nodes.new(type='ShaderNodeBsdfPrincipled')
principled_cube.location = (0, 0)

# Set properties for glossy red
principled_cube.inputs['Base Color'].default_value = (0.8, 0.02, 0.02, 1.0) # Vibrant Red
principled_cube.inputs['Roughness'].default_value = 0.05                   # Very glossy
principled_cube.inputs['IOR'].default_value = 1.45

# Link cube nodes
cube_links.new(principled_cube.outputs['BSDF'], cube_output.inputs['Surface'])

# Shade smooth for the cube to make gloss look nice
for polygon in cube.data.polygons:
    polygon.use_smooth = True
