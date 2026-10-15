import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create floor plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Create material for floor with checker texture
floor_mat = bpy.data.materials.new(name="FloorMaterial")
floor_mat.use_nodes = True
floor_mat.node_tree.nodes.clear()

# Add nodes for floor material
nodes = floor_mat.node_tree.nodes
links = floor_mat.node_tree.links

# Create checker texture node
checker = nodes.new(type='ShaderNodeTexChecker')
checker.inputs['Scale'].default_value = 10.0

# Create principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')

# Create material output
output = nodes.new(type='ShaderNodeOutputMaterial')

# Connect checker to base color
links.new(checker.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to floor
floor.data.materials.append(floor_mat)

# Create red glossy cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.5))
cube = bpy.context.active_object
cube.name = "RedCube"

# Create glossy red material for cube
cube_mat = bpy.data.materials.new(name="RedGlossy")
cube_mat.use_nodes = True
cube_mat.node_tree.nodes.clear()

# Add nodes for cube material
nodes_cube = cube_mat.node_tree.nodes
links_cube = cube_mat.node_tree.links

# Create principled BSDF for cube
principled_cube = nodes_cube.new(type='ShaderNodeBsdfPrincipled')
principled_cube.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # Red
principled_cube.inputs['Roughness'].default_value = 0.2  # Glossy (low roughness)

# Create material output for cube
output_cube = nodes_cube.new(type='ShaderNodeOutputMaterial')

# Connect principled to output
links_cube.new(principled_cube.outputs['BSDF'], output_cube.inputs['Surface'])

# Assign material to cube
cube.data.materials.append(cube_mat)
