import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a wooden plank (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
plank = bpy.context.active_object
plank.scale = (4, 0.5, 1)  # Scale to look like a plank
bpy.context.view_layer.objects.active = plank
plank.name = "WoodenPlank"

# Create a new material
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create nodes
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Texture nodes for the base color pattern
noise_texture = nodes.new(type='ShaderNodeTexNoise')
wave_texture = nodes.new(type='ShaderNodeTexWave')
color_ramp = nodes.new(type='ShaderNodeValRamp')
bump_node = nodes.new(type='ShaderNodeBump')

# Configure noise texture
noise_texture.inputs['Scale'].default_value = 15.0
noise_texture.inputs['Detail'].default_value = 5.0

# Configure wave texture
wave_texture.inputs['Scale'].default_value = 5.0
wave_texture.inputs['Distortion'].default_value = 1.0

# Configure color ramp for brown wood tones
color_ramp.color_ramp.elements[0].color = (0.3, 0.2, 0.1, 1.0)  # Dark brown
color_ramp.color_ramp.elements[1].color = (0.6, 0.4, 0.2, 1.0)  # Light brown

# Configure bump node
bump_node.inputs['Strength'].default_value = 0.5

# Connect nodes for base color
# Noise distorts the wave texture
links.new(noise_texture.outputs['Fac'], wave_texture.inputs['Distortion'])
# Wave output goes to color ramp
links.new(wave_texture.outputs['Fac'], color_ramp.inputs['Fac'])
# Color ramp output to base color
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

# Connect nodes for bump/normal
# Same distortion pattern drives bump
links.new(noise_texture.outputs['Fac'], bump_node.inputs['Height'])
# Bump output to normal
links.new(bump_node.outputs['Normal'], bsdf.inputs['Normal'])

# Connect BSDF to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to plank
plank.data.materials.append(mat)

# Set viewport shading to material preview or rendered to see the material
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
