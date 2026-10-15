import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a wooden plank (scaled cube)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
plank = bpy.context.active_object
plank.name = "WoodenPlank"
plank.scale = (3.0, 1.0, 0.15)
bpy.ops.object.transform_apply(scale=True)

# 3. Create procedural wood material
mat = bpy.data.materials.new(name="ProceduralWood")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = (600, 0)

node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
node_principled.location = (300, 0)
node_principled.inputs['Roughness'].default_value = 0.45

node_bump = nodes.new(type='ShaderNodeBump')
node_bump.location = (0, -200)
node_bump.inputs['Strength'].default_value = 0.15

node_color_ramp = nodes.new(type='ShaderNodeValToRGB')
node_color_ramp.location = (0, 150)

# Configure Color Ramp for wood tones
color_ramp = node_color_ramp.color_ramp
color_ramp.elements[0].position = 0.2
color_ramp.elements[0].color = (0.08, 0.03, 0.01, 1.0)  # Dark brown

color_ramp.elements.new(0.5)
color_ramp.elements[1].position = 0.5
color_ramp.elements[1].color = (0.22, 0.11, 0.04, 1.0)  # Medium brown

color_ramp.elements.new(0.8)
color_ramp.elements[2].position = 0.8
color_ramp.elements[2].color = (0.12, 0.05, 0.01, 1.0)  # Darker grain

node_wave = nodes.new(type='ShaderNodeTexWave')
node_wave.location = (-300, 150)
node_wave.wave_type = 'BANDS'
node_wave.bands_direction = 'Z'
node_wave.wave_profile = 'SIN'
node_wave.inputs['Scale'].default_value = 4.0
node_wave.inputs['Distortion'].default_value = 6.0
node_wave.inputs['Detail'].default_value = 2.0
node_wave.inputs['Detail Scale'].default_value = 1.0

node_noise = nodes.new(type='ShaderNodeTexNoise')
node_noise.location = (-600, 0)
node_noise.inputs['Scale'].default_value = 5.0
node_noise.inputs['Detail'].default_value = 4.0

node_mapping = nodes.new(type='ShaderNodeMapping')
node_mapping.location = (-900, 0)
node_mapping.inputs['Scale'].default_value = (1.0, 5.0, 1.0) # Stretch along the plank length

node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
node_tex_coord.location = (-1150, 0)

# 4. Link nodes together
# Texture coordinates and mapping
links.new(node_tex_coord.outputs['Object'], node_mapping.inputs['Vector'])
links.new(node_mapping.outputs['Vector'], node_noise.inputs['Vector'])

# Connect Noise to Wave distortion vector
links.new(node_noise.outputs['Color'], node_wave.inputs['Vector'])

# Color and Bump pathways from Wave Texture Fac
links.new(node_wave.outputs['Fac'], node_color_ramp.inputs['Fac'])
links.new(node_wave.outputs['Fac'], node_bump.inputs['Height'])

# Material connections
links.new(node_color_ramp.outputs['Color'], node_principled.inputs['Base Color'])
links.new(node_bump.outputs['Normal'], node_principled.inputs['Normal'])
links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

# 5. Assign material to plank
if plank.data.materials:
    plank.data.materials[0] = mat
else:
    plank.data.materials.append(mat)
