import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube and scale it to look like a plank
cube = bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
obj = bpy.context.active_object
obj.scale = (4, 0.2, 1)  # Scale to plank proportions

# Create a new material
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
mat.node_tree.nodes.clear()

# Create shader nodes
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Add nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
color_ramp = nodes.new(type='ShaderNodeValRamp')
bump_node = nodes.new(type='ShaderNodeBump')
noise_texture = nodes.new(type='ShaderNodeTexNoise')
wave_texture = nodes.new(type='ShaderNodeTexWave')
coord_node = nodes.new(type='ShaderNodeTexCoord')

# Configure Wave texture
wave_texture.inputs['Scale'].default_value = 5.0
wave_texture.inputs['Distortion'].default_value = 2.0

# Configure Noise texture for distortion
noise_texture.inputs['Scale'].default_value = 8.0
noise_texture.inputs['Detail'].default_value = 5.0

# Configure Color Ramp with brown tones
color_ramp.color_ramp.elements[0].color = (0.2, 0.1, 0.05, 1.0)  # Dark brown
color_ramp.color_ramp.elements[1].color = (0.6, 0.4, 0.2, 1.0)   # Light brown

# Configure Bump node
bump_node.inputs['Strength'].default_value = 0.8

# Configure Principled BSDF
principled.inputs['Roughness'].default_value = 0.7

# Connect nodes: Texture Coordinate -> Wave Texture
links.new(coord_node.outputs['Generated'], wave_texture.inputs['Vector'])

# Connect Noise Texture to Wave Texture's Distortion
links.new(coord_node.outputs['Generated'], noise_texture.inputs['Vector'])
links.new(noise_texture.outputs['Fac'], wave_texture.inputs['Distortion'])

# Connect Wave output through Color Ramp to Base Color
links.new(wave_texture.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])

# Connect Wave output to Bump for normal mapping
links.new(wave_texture.outputs['Fac'], bump_node.inputs['Height'])
links.new(bump_node.outputs['Normal'], principled.inputs['Normal'])

# Connect Principled to Output
links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to object
obj.data.materials.append(mat)
