import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create the wooden plank (a scaled cube)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
plank = bpy.active_object
plank.name = "Wooden_Plank"

# Scale the cube into a plank shape (long, wide, thin)
plank.scale = (3.5, 1.2, 0.15)
bpy.ops.object.transform_apply(scale=True)

# 3. Create procedural wood material
material = bpy.data.materials.new(name="Procedural_Wood_Material")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
nodes.clear()

# Create necessary nodes
node_tex_coord = nodes.node_type_default = nodes.new(type='ShaderNodeTexCoord')
node_tex_coord.location = (-900, 0)

node_mapping = nodes.new(type='ShaderNodeMapping')
node_mapping.location = (-700, 0)
# Optional: scale the mapping to stretch the wood grain along the plank length
node_mapping.inputs['Scale'].default_value = (1.0, 4.0, 4.0)

node_noise = nodes.new(type='ShaderNodeTexNoise')
node_noise.location = (-500, 150)
node_noise.inputs['Scale'].default_value = 3.5
node_noise.inputs['Detail'].default_value = 4.0
node_noise.inputs['Roughness'].default_value = 0.5

node_wave = nodes.new(type='ShaderNodeTexWave')
node_wave.location = (-300, 0)
node_wave.wave_type = 'BANDS'
node_wave.bands_direction = 'Z'
node_wave.wave_profile = 'SIN'
node_wave.inputs['Scale'].default_value = 2.5
node_wave.inputs['Distortion'].default_value = 4.0
node_wave.inputs['Detail'].default_value = 2.0

node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
node_color_ramp.location = (-50, 200)
# Configure Color Ramp for rich wood tones
# Element 0: Dark brown (grooves / deep grain)
node_color_ramp.color_ramp.elements[0].position = 0.2
node_color_ramp.color_ramp.elements[0].color = (0.08, 0.04, 0.01, 1.0)

# Element 1: Warm light brown (base wood tone)
node_color_ramp.color_ramp.elements.new(0.6)
node_color_ramp.color_ramp.elements[1].position = 0.55
node_color_ramp.color_ramp.elements[1].color = (0.32, 0.18, 0.08, 1.0)

# Add a highlight tone for variety
node_color_ramp.color_ramp.elements.new(1.0)
node_color_ramp.color_ramp.elements[2].position = 0.85
node_color_ramp.color_ramp.elements[2].color = (0.45, 0.27, 0.13, 1.0)

node_bump = nodes.new(type='ShaderNodeBump')
node_bump.location = (-50, -100)
node_bump.inputs['Strength'].default_value = 0.15
node_bump.inputs['Distance'].default_value = 0.05

node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
node_principled.location = (250, 100)
# Slightly reduce roughness for a polished wood look
node_principled.inputs['Roughness'].default_value = 0.35

node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = (550, 100)

# 4. Link the nodes together
# Texture Coordinate -> Mapping -> Wave (Vector distortion via Noise)
links.new(node_tex_coord.outputs['Object'], node_mapping.inputs['Vector'])
links.new(node_mapping.outputs['Vector'], node_noise.inputs['Vector'])

# Feed the noise color output into the wave texture vector/distortion input
links.new(node_noise.outputs['Color'], node_wave.inputs['Vector'])

# Wave Fac -> Color Ramp (Base Color)
links.new(node_wave.outputs['Fac'], node_color_ramp.inputs['Fac'])
links.new(node_color_ramp.outputs['Color'], node_principled.inputs['Base Color'])

# Wave Fac -> Bump Height -> Normal
links.new(node_wave.outputs['Fac'], node_bump.inputs['Height'])
links.new(node_bump.outputs['Normal'], node_principled.inputs['Normal'])

# Principled BSDF -> Material Output
links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

# 5. Assign material to the plank
plank.data.materials.append(material)

# Ensure smooth shading on the plank for proper normal visualization
for polygon in plank.data.polygons:
    polygon.use_smooth = True
