import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add Suzanne mesh
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
bpy.ops.object.delete()

# Add Suzanne using the proper operator
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
suzanne = bpy.context.active_object

# Create a new material
material = bpy.data.materials.new(name="White Marble")
material.use_nodes = True

# Clear default nodes
material.node_tree.nodes.clear()

# Create nodes
nodes = material.node_tree.nodes
links = material.node_tree.links

# Add Principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')

# Add Material Output
material_output = nodes.new(type='ShaderNodeOutputMaterial')

# Add Noise Texture
noise_texture = nodes.new(type='ShaderNodeTexNoise')
noise_texture.inputs['Detail'].default_value = 5.0
noise_texture.inputs['Roughness'].default_value = 0.6

# Add Color Ramp
color_ramp = nodes.new(type='ShaderNodeValRamp')
# Set color ramp to white marble-like gradient
color_ramp.color_ramp.elements[0].color = (0.3, 0.3, 0.3, 1.0)  # Dark gray
color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # White

# Add Coordinate node for texture mapping
coord = nodes.new(type='ShaderNodeTexCoord')

# Add Mapping node for scale control
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (5.0, 5.0, 5.0)

# Connect nodes
links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise_texture.inputs['Vector'])
links.new(noise_texture.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], material_output.inputs['Surface'])

# Set principled BSDF properties for marble look
principled.inputs['Roughness'].default_value = 0.3
principled.inputs['Specular IOR'].default_value = 1.5

# Assign material to Suzanne
suzanne.data.materials.append(material)

# Set viewport shading to Material Preview or Rendered for better visualization
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
