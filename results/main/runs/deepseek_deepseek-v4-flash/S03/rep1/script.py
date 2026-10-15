import bpy

# Remove all existing objects safely
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create Suzanne (monkey) mesh
bpy.ops.mesh.primitive_monkey_add(size=2, location=(0, 0, 0))
obj = bpy.context.object

# Create white marble material
mat = bpy.data.materials.new(name="White_Marble")
mat.use_nodes = True
nt = mat.node_tree
nodes = nt.nodes
links = nt.links

# Clear default nodes
nodes.clear()

# Create nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (300, 0)

principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.location = (0, 0)

noise = nodes.new(type='ShaderNodeTexNoise')
noise.location = (-600, 0)
# Configure noise scale/detail/distortion via input sockets
noise.inputs['Scale'].default_value = 2.0
noise.inputs['Detail'].default_value = 1.0
noise.inputs['Distortion'].default_value = 0.6

color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (-300, 0)
# Light gray to white (white marble look)
ramp_elements = color_ramp.color_ramp.elements
ramp_elements[0].color = (0.7, 0.7, 0.7, 1.0)
ramp_elements[1].color = (1.0, 1.0, 1.0, 1.0)

# Link nodes
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to Suzanne
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
