import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Add Suzanne (Monkey) mesh
bpy.ops.mesh.primitive_monkey_add(size=2.0, location=(0, 0, 0))
suzanne = bpy.context.active_object

# Smooth shading for better appearance
for face in suzanne.data.polygons:
    face.use_smooth = True

# 3. Create White Marble Material using procedural nodes
material = bpy.data.materials.new(name="WhiteMarble")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create Principled BSDF and Material Output
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (100, 0)
principled_node.inputs['Roughness'].default_value = 0.15  # Glossy marble look

# Create Texture Coordinate and Mapping nodes for procedural placement
tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
tex_coord_node.location = (-700, 0)

mapping_node = nodes.new(type='ShaderNodeMapping')
mapping_node.location = (-500, 0)
mapping_node.inputs['Scale'].default_value = (1.5, 1.5, 1.5)

# Create Wave Texture to emulate marble veins
wave_node = nodes.new(type='ShaderNodeTexWave')
wave_node.location = (-300, 0)
wave_node.wave_type = 'BANDS'
wave_node.bands_direction = 'DIAGONAL'
wave_node.wave_profile = 'SIN'
wave_node.inputs['Scale'].default_value = 3.5
wave_node.inputs['Distortion'].default_value = 7.0
wave_node.inputs['Detail'].default_value = 4.0

# Create Color Ramp to map wave output to marble colors (White and Dark Grey/Blue veins)
color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
color_ramp_node.location = (-100, 0)

# Configure Color Ramp elements
color_ramp = color_ramp_node.color_ramp
color_ramp.elements[0].position = 0.35
color_ramp.elements[0].color = (0.05, 0.05, 0.06, 1.0)  # Dark vein

# Add a second element for the transition to white
elem_middle = color_ramp.elements.new(0.48)
elem_middle.color = (0.7, 0.7, 0.72, 1.0)

color_ramp.elements[1].position = 0.65
color_ramp.elements[1].color = (0.95, 0.95, 0.96, 1.0)  # White marble base

# Link procedural texture nodes together
links.new(tex_coord_node.outputs['Object'], mapping_node.inputs['Vector'])
links.new(mapping_node.outputs['Vector'], wave_node.inputs['Vector'])
links.new(wave_node.outputs['Color'], color_ramp_node.inputs['Fac'])

# Link Color Ramp to Principled BSDF Base Color
links.new(color_ramp_node.outputs['Color'], principled_node.inputs['Base Color'])

# Link Principled BSDF to Material Output
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# 4. Assign Material to Suzanne
if suzanne.data.materials:
    suzanne.data.materials[0] = material
else:
    suzanne.data.materials.append(material)

# Select Suzanne as active object
bpy.context.view_layer.objects.active = suzanne
suzanne.select_set(True)
