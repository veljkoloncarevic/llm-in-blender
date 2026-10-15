import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
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

# Create shader nodes
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
checker = nodes.new(type='ShaderNodeTexChecker')
color_ramp = nodes.new(type='ShaderNodeValRamp')

# Connect checker texture to color ramp to get black and white
links.new(checker.outputs['Fac'], color_ramp.inputs['Fac'])

# Connect color ramp to Base Color
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

# Connect BSDF to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Set checker scale
checker.inputs['Scale'].default_value = 5.0

# Apply material to floor
floor.data.materials.append(floor_mat)

# Create glossy red cube
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
cube = bpy.context.active_object
cube.name = "Cube"

# Create glossy red material for cube
cube_mat = bpy.data.materials.new(name="CubeMaterial")
cube_mat.use_nodes = True
cube_mat.node_tree.nodes.clear()

# Add nodes for cube material
cube_nodes = cube_mat.node_tree.nodes
cube_links = cube_mat.node_tree.links

# Create shader nodes for glossy red
cube_bsdf = cube_nodes.new(type='ShaderNodeBsdfPrincipled')
cube_output = cube_nodes.new(type='ShaderNodeOutputMaterial')

# Set base color to red
cube_bsdf.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)

# Increase roughness for glossy appearance (lower roughness = more glossy)
cube_bsdf.inputs['Roughness'].default_value = 0.2

# Connect to output
cube_links.new(cube_bsdf.outputs['BSDF'], cube_output.inputs['Surface'])

# Apply material to cube
cube.data.materials.append(cube_mat)
