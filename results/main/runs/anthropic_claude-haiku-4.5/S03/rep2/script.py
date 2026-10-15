import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add Suzanne mesh
bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0))
suzanne_obj = bpy.context.active_object
bpy.ops.object.delete(use_global=False)

# Add Suzanne using the correct operator
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
suzanne_obj = bpy.context.active_object
suzanne_obj.name = "Suzanne"

# Create material
mat = bpy.data.materials.new(name="WhiteMarble")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create shader nodes
# Noise Texture
noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.inputs['Detail'].default_value = 5.0
noise_node.inputs['Roughness'].default_value = 0.7

# Color Ramp
color_ramp = nodes.new(type='ShaderNodeValRamp')
color_ramp.color_ramp.elements[0].color = (0.1, 0.1, 0.1, 1.0)  # Dark gray
color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)  # White

# Principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
principled.inputs['Roughness'].default_value = 0.2
principled.inputs['Specular IOR'].default_value = 1.5

# Material Output
output_node = nodes.new(type='ShaderNodeOutputMaterial')

# Connect nodes
links.new(noise_node.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to Suzanne
suzanne_obj.data.materials.append(mat)

# Set viewport shading to show materials
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
