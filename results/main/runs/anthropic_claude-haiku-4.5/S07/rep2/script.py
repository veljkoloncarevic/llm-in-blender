import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 0))
cylinder = bpy.context.active_object

# Create a new material
mat = bpy.data.materials.new(name="RustyMetal")
mat.use_nodes = True

# Clear default nodes
mat.node_tree.nodes.clear()

# Create nodes
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

# Mix Shader node
mix_shader = nodes.new(type='ShaderNodeMix')
mix_shader.location = (200, 0)
mix_shader.data_type = 'SHADER'

# Principled BSDF for metallic grey
metal_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
metal_shader.location = (0, 100)
metal_shader.inputs['Base Color'].default_value = (0.5, 0.5, 0.52, 1.0)  # Grey
metal_shader.inputs['Metallic'].default_value = 1.0
metal_shader.inputs['Roughness'].default_value = 0.3

# Principled BSDF for rust (orange-brown)
rust_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
rust_shader.location = (0, -100)
rust_shader.inputs['Base Color'].default_value = (0.8, 0.4, 0.1, 1.0)  # Orange-brown
rust_shader.inputs['Metallic'].default_value = 0.2
rust_shader.inputs['Roughness'].default_value = 0.8

# Noise Texture for mask
noise_texture = nodes.new(type='ShaderNodeTexNoise')
noise_texture.location = (-200, -50)
noise_texture.inputs['Scale'].default_value = 15.0
noise_texture.inputs['Detail'].default_value = 5.0
noise_texture.inputs['Roughness'].default_value = 0.5

# ColorRamp to control the mask contrast
color_ramp = nodes.new(type='ShaderNodeValRamp')
color_ramp.location = (-50, -50)
color_ramp.color_ramp.elements[0].position = 0.3
color_ramp.color_ramp.elements[1].position = 0.7

# Connect nodes
links.new(metal_shader.outputs['BSDF'], mix_shader.inputs[1])
links.new(rust_shader.outputs['BSDF'], mix_shader.inputs[2])
links.new(noise_texture.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], mix_shader.inputs['A'])
links.new(mix_shader.outputs['Result'], output_node.inputs['Surface'])

# Assign material to cylinder
cylinder.data.materials.append(mat)

# Add smooth shading
bpy.context.view_layer.objects.active = cylinder
bpy.ops.object.shade_smooth()
