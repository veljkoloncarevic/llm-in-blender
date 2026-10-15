import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add Suzanne mesh
bpy.ops.mesh.primitive_uv_sphere_add()
bpy.ops.object.delete(use_global=False)

bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
suzanne = bpy.context.active_object

# Create a new material
mat = bpy.data.materials.new(name="MarbleMaterial")
mat.use_nodes = True

# Clear default nodes
mat.node_tree.nodes.clear()

# Create nodes
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Add Principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')

# Add Noise Texture
noise = nodes.new(type='ShaderNodeTexNoise')
noise.inputs['Detail'].default_value = 5.0
noise.inputs['Roughness'].default_value = 0.7

# Add Color Ramp
color_ramp = nodes.new(type='ShaderNodeValRamp')
color_ramp.color_ramp.elements[0].color = (0.9, 0.9, 0.9, 1.0)  # Light gray/white
color_ramp.color_ramp.elements[1].color = (0.3, 0.3, 0.3, 1.0)  # Dark gray

# Add ColorRamp for RGB output
color_ramp_rgb = nodes.new(type='ShaderNodeValRamp')
color_ramp_rgb.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)  # White
color_ramp_rgb.color_ramp.elements[1].color = (0.7, 0.7, 0.7, 1.0)  # Light gray

# Set Principled BSDF properties for marble
principled.inputs['Roughness'].default_value = 0.2
principled.inputs['Specular IOR'].default_value = 1.5

# Connect nodes
# Noise Fac output to Color Ramp Fac input
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])

# Color Ramp Color output to Principled Base Color
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])

# Principled BSDF to Material Output
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to Suzanne
suzanne.data.materials.append(mat)

# Add Coordinate and Mapping for better texture control
coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')

# Connect Coordinate to Mapping to Noise
links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

# Set mapping scale for better marble pattern
mapping.inputs['Scale'].default_value = (5.0, 5.0, 5.0)
