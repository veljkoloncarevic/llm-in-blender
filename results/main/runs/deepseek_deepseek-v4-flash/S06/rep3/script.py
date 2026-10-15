import bpy

# Remove all existing objects
if bpy.context.scene.objects:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Create a wooden plank (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
plank = bpy.context.active_object
plank.name = "WoodPlank"
plank.scale = (4.0, 0.2, 1.0)

# Create procedural wood material
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
ntree = mat.node_tree
nodes = ntree.nodes
links = ntree.links

# Clear default nodes
nodes.clear()

# Create the necessary nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
noise_node = nodes.new(type='ShaderNodeTexNoise')
wave_node = nodes.new(type='ShaderNodeTexWave')
color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
bump_node = nodes.new(type='ShaderNodeBump')

# Arrange nodes for readability (optional)
output_node.location = (300, 0)
principled_node.location = (100, 0)
tex_coord_node.location = (-800, 0)
noise_node.location = (-600, 200)
wave_node.location = (-400, 0)
color_ramp_node.location = (-100, 0)
bump_node.location = (100, -200)

# Configure the Wave Texture for wood grain along X
wave_node.wave_type = 'BANDS'
wave_node.bands_direction = 'Z'      # Vary along Z so grain lines run along X
wave_node.scale = 10.0
wave_node.distortion = 1.0

# Noise distorts the wave
noise_node.scale = 2.0

# Brown ColorRamp tones
color_ramp_node.color_ramp.elements[0].position = 0.0
color_ramp_node.color_ramp.elements[0].color = (0.05, 0.02, 0.01, 1.0)   # very dark brown
mid_elem = color_ramp_node.color_ramp.elements.new(0.4)
mid_elem.color = (0.3, 0.16, 0.07, 1.0)                                  # medium brown
color_ramp_node.color_ramp.elements[1].position = 1.0
color_ramp_node.color_ramp.elements[1].color = (0.85, 0.65, 0.4, 1.0)    # light brown

# Bump node settings
bump_node.strength = 0.1
bump_node.distance = 0.001

# Make the surface look like matte wood
principled_node.inputs['Roughness'].default_value = 0.6

# Connect the nodes
links.new(tex_coord_node.outputs['Generated'], noise_node.inputs['Vector'])
links.new(tex_coord_node.outputs['Generated'], wave_node.inputs['Vector'])
links.new(noise_node.outputs['Fac'], wave_node.inputs['Distortion'])

# The same wave pattern goes to both the color ramp and the bump height
links.new(wave_node.outputs['Fac'], color_ramp_node.inputs['Fac'])
links.new(wave_node.outputs['Fac'], bump_node.inputs['Height'])

# Color ramp to Base Color, bump to Normal
links.new(color_ramp_node.outputs['Color'], principled_node.inputs['Base Color'])
links.new(bump_node.outputs['Normal'], principled_node.inputs['Normal'])

# Principled BSDF to Material Output
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to the plank
if plank.data.materials:
    plank.data.materials[0] = mat
else:
    plank.data.materials.append(mat)
