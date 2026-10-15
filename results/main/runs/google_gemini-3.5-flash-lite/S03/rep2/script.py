import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Add Suzanne (Monkey) mesh
bpy.ops.mesh.primitive_monkey_add(size=2.0, location=(0, 0, 0))
suzanne = bpy.context.active_object

# Smooth shading for a better look
for poly in suzanne.data.polygons:
    poly.use_smooth = True

# 3. Create White Marble Material using procedural nodes
material = bpy.data.materials.new(name="WhiteMarble")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes to build custom shader network cleanly
nodes.clear()

# Create Principled BSDF and Material Output nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (100, 0)
# Tweak principled BSDF settings for marble finish
principled_node.inputs['Roughness'].default_value = 0.15

# Create Texture Coordinate and Mapping nodes for controlled texturing
tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
tex_coord_node.location = (-700, 0)

mapping_node = nodes.new(type='ShaderNodeMapping')
mapping_node.location = (-500, 0)
mapping_node.inputs['Scale'].default_value = (3.0, 3.0, 3.0)

# Create Wave Texture for marble banding
wave_node = nodes.new(type='ShaderNodeTexWave')
wave_node.location = (-300, 0)
wave_node.wave_type = 'BANDS'
wave_node.bands_direction = 'DIAGONAL'
wave_node.inputs['Scale'].default_value = 2.5
wave_node.inputs['Distortion'].default_value = 6.0
wave_node.inputs['Detail'].default_value = 4.0

# Create Color Ramp to map wave output to marble colors
color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
color_ramp_node.location = (-100, 0)

# Configure Color Ramp: White base with sharp dark veins
color_ramp_node.color_ramp.elements[0].position = 0.35
color_ramp_node.color_ramp.elements[0].color = (0.95, 0.95, 0.95, 1.0) # White

color_ramp_node.color_ramp.elements.new(0.5)
color_ramp_node.color_ramp.elements[1].position = 0.48
color_ramp_node.color_ramp.elements[1].color = (0.1, 0.1, 0.1, 1.0) # Dark Vein

color_ramp_node.color_ramp.elements.new(0.7)
color_ramp_node.color_ramp.elements[2].position = 0.65
color_ramp_node.color_ramp.elements[2].color = (0.9, 0.9, 0.9, 1.0) # Back to White

# 4. Link Nodes Together
links.new(tex_coord_node.outputs['Object'], mapping_node.inputs['Vector'])
links.new(mapping_node.outputs['Vector'], wave_node.inputs['Vector'])
links.new(wave_node.outputs['Color'], color_ramp_node.inputs['Fac'])
links.new(color_ramp_node.outputs['Color'], principled_node.inputs['Base Color'])
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# 5. Assign Material to Suzanne
if suzanne.data.materials:
    suzanne.data.materials[0] = material
else:
    suzanne.data.materials.append(material)
