import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add Suzanne
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
monkey = bpy.context.object
monkey.name = "Suzanne"
bpy.ops.object.shade_smooth()

# Create marble material
mat = bpy.data.materials.new(name="White_Marble")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

# Add nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
noise = nodes.new(type='ShaderNodeTexNoise')
color_ramp = nodes.new(type='ShaderNodeValToRGB')

# Position nodes (for clarity)
output.location = (300, 0)
principled.location = (100, 0)
color_ramp.location = (-100, 0)
noise.location = (-300, 0)

# Configure noise
noise.noise_dimensions = '3D'
noise.scale = 3.0
noise.detail = 8.0

# Configure color ramp: dark veins to white
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1.0)
color_ramp.color_ramp.elements[1].position = 1.0
color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

# Configure Principled BSDF for marble look
principled.inputs['Roughness'].default_value = 0.25
principled.inputs['Specular IOR Level'].default_value = 0.5

# Link nodes
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to Suzanne
if monkey.data.materials:
    monkey.data.materials[0] = mat
else:
    monkey.data.materials.append(mat)
