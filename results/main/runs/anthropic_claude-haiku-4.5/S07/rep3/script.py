import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 0))
cylinder = bpy.context.active_object

# Create a new material
mat = bpy.data.materials.new(name="RustyMetal")
mat.use_nodes = True
mat.blend_method = 'BLEND'

# Clear default nodes
nodes = mat.node_tree.nodes
nodes.clear()

# Create shader nodes
links = mat.node_tree.links

# Main output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

# Mix Shader to blend metallic and rust
mix_shader = nodes.new(type='ShaderNodeMixShader')
mix_shader.location = (200, 0)
links.new(mix_shader.outputs[0], output_node.inputs[0])

# Principled BSDF for metallic surface (grey)
metallic_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
metallic_shader.location = (0, 100)
metallic_shader.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)  # Grey
metallic_shader.inputs['Metallic'].default_value = 1.0
metallic_shader.inputs['Roughness'].default_value = 0.3
links.new(metallic_shader.outputs[0], mix_shader.inputs[1])

# Principled BSDF for rust surface (orange-brown)
rust_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
rust_shader.location = (0, -100)
rust_shader.inputs['Base Color'].default_value = (0.8, 0.4, 0.1, 1.0)  # Orange-brown
rust_shader.inputs['Metallic'].default_value = 0.2
rust_shader.inputs['Roughness'].default_value = 0.8
links.new(rust_shader.outputs[0], mix_shader.inputs[2])

# Noise texture as mask
noise_texture = nodes.new(type='ShaderNodeTexNoise')
noise_texture.location = (-200, 0)
noise_texture.inputs['Scale'].default_value = 15.0
noise_texture.inputs['Detail'].default_value = 5.0
noise_texture.inputs['Roughness'].default_value = 0.5

# ColorRamp to control the mix factor
color_ramp = nodes.new(type='ShaderNodeValRamp')
color_ramp.location = (-50, 0)
color_ramp.color_ramp.elements[0].position = 0.3
color_ramp.color_ramp.elements[1].position = 0.7
links.new(noise_texture.outputs['Fac'], color_ramp.inputs[0])
links.new(color_ramp.outputs[0], mix_shader.inputs[0])

# Add texture coordinates
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-400, 0)
links.new(tex_coord.outputs[0], noise_texture.inputs[0])

# Assign material to cylinder
cylinder.data.materials.append(mat)

# Smooth shading for better appearance
bpy.context.view_layer.objects.active = cylinder
bpy.ops.object.shade_smooth()
