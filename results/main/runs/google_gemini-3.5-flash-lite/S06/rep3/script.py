import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a wooden plank (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
plank = bpy.context.active_object
plank.name = "WoodenPlank"
# Scale to plank dimensions: length, width, thickness
plank.scale = (2.0, 0.6, 0.1)

# Apply scale so procedural texture mapping is even
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 3. Create procedural wood material
mat = bpy.data.materials.new(name="ProceduralWood")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add Output node
material_output = nodes.new(type='ShaderNodeOutputMaterial')
material_output.location = (600, 0)

# Add Principled BSDF node
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.location = (300, 0)
principled.inputs['Roughness'].default_value = 0.45
links.new(principled.outputs['BSDF'], material_output.inputs['Surface'])

# Add Texture Coordinate node
tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.location = (-900, 0)

# Add Mapping node
mapping = nodes.new(type='ShaderNodeMapping')
mapping.location = (-700, 0)
# Scale the mapping to stretch the wood grain along the plank length
mapping.inputs['Scale'].default_value = (1.0, 5.0, 5.0)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Add Noise Texture node (for distortion)
noise_tex = nodes.new(type='ShaderNodeTexNoise')
noise_tex.location = (-500, 200)
noise_tex.inputs['Scale'].default_value = 5.0
noise_tex.inputs['Detail'].default_value = 4.0
links.new(mapping.outputs['Vector'], noise_tex.inputs['Vector'])

# Add Mix Color node to mix mapping coordinates with the noise distortion
# (using Mix Color / Mix RGB to offset the vector)
mix_node = nodes.new(type='ShaderNodeMix')
mix_node.data_type = 'VECTOR'
mix_node.location = (-300, 100)
mix_node.blend_type = 'ADD'
mix_node.inputs['Factor'].default_value = 0.3  # Strength of distortion
links.new(mapping.outputs['Vector'], mix_node.inputs[4])  # A
links.new(noise_tex.outputs['Color'], mix_node.inputs[5]) # B

# Add Wave Texture node (driven by distorted coordinates)
wave_tex = nodes.new(type='ShaderNodeTexWave')
wave_tex.location = (-100, 100)
wave_tex.wave_type = 'BANDS'
wave_tex.bands_direction = 'Z'
wave_tex.wave_profile = 'SIN'
wave_tex.inputs['Scale'].default_value = 3.5
wave_tex.inputs['Distortion'].default_value = 2.0
wave_tex.inputs['Detail'].default_value = 2.0
links.new(mix_node.outputs['Vector'], wave_tex.inputs['Vector'])

# Add Color Ramp node for brown tones (Base Color)
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (100, 200)
# Configure Color Ramp elements for wood tones
color_ramp.color_ramp.elements[0].position = 0.2
color_ramp.color_ramp.elements[0].color = (0.08, 0.04, 0.01, 1.0) # Dark brown

# Add a middle stop for variation
elem_mid = color_ramp.color_ramp.elements.new(0.5)
elem_mid.color = (0.22, 0.12, 0.05, 1.0) # Medium warm brown

color_ramp.color_ramp.elements[1].position = 0.8
color_ramp.color_ramp.elements[1].color = (0.42, 0.25, 0.12, 1.0) # Lighter wood tone

links.new(wave_tex.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])

# Add Bump node for normal map effect
bump = nodes.new(type='ShaderNodeBump')
bump.location = (100, -150)
bump.inputs['Strength'].default_value = 0.15
links.new(wave_tex.outputs['Color'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], principled.inputs['Normal'])

# Assign material to the plank
plank.data.materials.append(mat)
