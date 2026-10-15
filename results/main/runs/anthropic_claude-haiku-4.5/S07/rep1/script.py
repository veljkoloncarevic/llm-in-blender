import bpy
import bmesh
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 0, 0))
cylinder = bpy.context.active_object

# Create a new material
mat = bpy.data.materials.new(name="RustyMetal")
mat.use_nodes = True
mat.diffuse_color = (0.5, 0.5, 0.5, 1.0)

# Clear default nodes
nodes = mat.node_tree.nodes
nodes.clear()

# Create shader nodes
links = mat.node_tree.links

# Main output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (600, 0)

# Mix shader for blending metallic and rust
mix_shader = nodes.new(type='ShaderNodeMix')
mix_shader.location = (400, 0)
mix_shader.data_type = 'SHADER'

# Metallic shader (grey)
metallic_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
metallic_shader.location = (200, 100)
metallic_shader.inputs['Base Color'].default_value = (0.4, 0.4, 0.45, 1.0)
metallic_shader.inputs['Metallic'].default_value = 1.0
metallic_shader.inputs['Roughness'].default_value = 0.3

# Rust shader (orange-brown)
rust_shader = nodes.new(type='ShaderNodeBsdfPrincipled')
rust_shader.location = (200, -150)
rust_shader.inputs['Base Color'].default_value = (0.7, 0.4, 0.1, 1.0)
rust_shader.inputs['Metallic'].default_value = 0.2
rust_shader.inputs['Roughness'].default_value = 0.8

# Noise texture for mask
noise_texture = nodes.new(type='ShaderNodeTexNoise')
noise_texture.location = (-200, -100)
noise_texture.inputs['Detail'].default_value = 5.0
noise_texture.inputs['Roughness'].default_value = 0.6
noise_texture.inputs['Scale'].default_value = 5.0

# Coordinate mapping for texture
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-400, -100)

# Connect nodes
links.new(tex_coord.outputs['Generated'], noise_texture.inputs['Vector'])
links.new(noise_texture.outputs['Fac'], mix_shader.inputs['Factor'])

links.new(metallic_shader.outputs['BSDF'], mix_shader.inputs[1])
links.new(rust_shader.outputs['BSDF'], mix_shader.inputs[2])

links.new(mix_shader.outputs['Result'], output_node.inputs['Surface'])

# Assign material to cylinder
cylinder.data.materials.append(mat)

# Set viewport shading to Material Preview or Rendered to see the result
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
