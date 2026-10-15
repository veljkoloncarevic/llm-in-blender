import bpy
import bmesh
from mathutils import Vector

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create floor plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Create material for floor with checker texture
floor_material = bpy.data.materials.new(name="FloorMaterial")
floor_material.use_nodes = True
floor_material.node_tree.nodes.clear()

# Create nodes for floor material
nodes = floor_material.node_tree.nodes
links = floor_material.node_tree.links

# Add shader nodes
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')
checker = nodes.new(type='ShaderNodeTexChecker')
color_ramp = nodes.new(type='ShaderNodeValRamp')

# Configure checker texture
checker.inputs['Scale'].default_value = 10.0

# Configure color ramp to output black and white
color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)  # Black
color_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)  # White

# Connect nodes
links.new(checker.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to floor
floor.data.materials.append(floor_material)

# Create red glossy cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "RedCube"

# Create material for cube
cube_material = bpy.data.materials.new(name="RedGlossy")
cube_material.use_nodes = True
cube_material.node_tree.nodes.clear()

# Create nodes for cube material
cube_nodes = cube_material.node_tree.nodes
cube_links = cube_material.node_tree.links

# Add shader nodes for glossy red cube
cube_bsdf = cube_nodes.new(type='ShaderNodeBsdfPrincipled')
cube_output = cube_nodes.new(type='ShaderNodeOutputMaterial')

# Configure for glossy red appearance
cube_bsdf.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # Red
cube_bsdf.inputs['Roughness'].default_value = 0.2  # Glossy

# Connect nodes
cube_links.new(cube_bsdf.outputs['BSDF'], cube_output.inputs['Surface'])

# Assign material to cube
cube.data.materials.append(cube_material)
