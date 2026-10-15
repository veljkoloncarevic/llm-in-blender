import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create Suzanne the monkey mesh
bpy.ops.mesh.primitive_monkey_add(size=2.0, location=(0, 0, 0))
suzanne = bpy.active_object
suzanne.name = "MarbleSuzanne"

# Smooth shading for Suzanne
for poly in suzanne.data.polygons:
    poly.use_smooth = True

# Create a new material for white marble
mat = bpy.data.materials.new(name="WhiteMarbleMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes to build our own setup
nodes.clear()

# Add Output Node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (400, 0)

# Add Principled BSDF
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (100, 0)
# Set some subtle properties for marble look
principled_node.inputs['Roughness'].default_value = 0.15
principled_node.inputs['IOR'].default_value = 1.45

# Add Wave Texture (gives a great natural marble banding look)
wave_node = nodes.new(type='ShaderNodeTexWave')
wave_node.location = (-450, 0)
wave_node.wave_type = 'BANDS'
wave_node.bands_direction = 'Z'
wave_node.wave_profile = 'SIN'
wave_node.scale = 3.0
wave_node.distortion = 7.0
wave_node.detail = 4.0

# Add Texture Coordinate to drive the Wave Texture mapping
tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
tex_coord_node.location = (-650, 0)

# Add Color Ramp for controlling the marble veins and base white
color_ramp_node = nodes.new(type='ShaderNodeValToRGB')
color_ramp_node.location = (-150, 0)

# Configure Color Ramp: Black veins on a white background
# Element 0: Dark gray/black for veins
color_ramp_node.color_ramp.elements[0].position = 0.35
color_ramp_node.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)

# Element 1: Pure white for the marble body
color_ramp_node.color_ramp.elements[1].position = 0.65
color_ramp_node.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1.0)

# Link nodes together
# Tex Coord (Object) -> Wave Texture (Vector)
links.new(tex_coord_node.outputs['Object'], wave_node.inputs['Vector'])

# Wave Texture (Color) -> Color Ramp (Fac)
links.new(wave_node.outputs['Color'], color_ramp_node.inputs['Fac'])

# Color Ramp (Color) -> Principled BSDF (Base Color)
links.new(color_ramp_node.outputs['Color'], principled_node.inputs['Base Color'])

# Principled BSDF (BSDF) -> Material Output (Surface)
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to Suzanne
if suzanne.data.materials:
    suzanne.data.materials[0] = mat
else:
    suzanne.data.materials.append(mat)
