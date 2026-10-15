import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add Suzanne
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
suzanne = bpy.context.object

# Create white marble material
mat = bpy.data.materials.new(name="White_Marble")
mat.use_nodes = True
ntree = mat.node_tree
nodes = ntree.nodes
links = ntree.links

# Clear default nodes
nodes.clear()

# Create nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
noise = nodes.new(type='ShaderNodeTexNoise')
ramp = nodes.new(type='ShaderNodeValToRGB')

# Position nodes
output.location = (400, 0)
principled.location = (200, 0)
ramp.location = (0, 0)
noise.location = (-200, 0)

# Configure noise texture
noise.inputs['Scale'].default_value = 4.0
noise.inputs['Detail'].default_value = 2.0
noise.inputs['Roughness'].default_value = 0.5

# Configure color ramp for white marble look
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.75, 0.75, 0.75, 1)
ramp.color_ramp.elements[1].position = 1.0
ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

# Configure principled BSDF
principled.inputs['Roughness'].default_value = 0.3

# Connect nodes
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to Suzanne
if suzanne.data.materials:
    suzanne.data.materials[0] = mat
else:
    suzanne.data.materials.append(mat)
