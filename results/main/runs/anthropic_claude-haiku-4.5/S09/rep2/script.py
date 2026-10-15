import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
sphere = bpy.context.active_object

# Create a new material
material = bpy.data.materials.new(name="CarPaint")
material.use_nodes = True

# Clear default nodes
material.node_tree.nodes.clear()

# Create nodes
nodes = material.node_tree.nodes
links = material.node_tree.links

# Add Principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.location = (0, 0)

# Set base color to deep red
principled.inputs['Base Color'].default_value = (0.5, 0.02, 0.02, 1.0)

# Set metallic to 0.5
principled.inputs['Metallic'].default_value = 0.5

# Set roughness for a car paint look
principled.inputs['Roughness'].default_value = 0.15

# Enable and configure the coat weight (clear coat)
principled.inputs['Coat Weight'].default_value = 0.85

# Set coat roughness for a glossy clear coat
principled.inputs['Coat Roughness'].default_value = 0.1

# Add Material Output node
material_output = nodes.new(type='ShaderNodeOutputMaterial')
material_output.location = (400, 0)

# Connect Principled BSDF to Material Output
links.new(principled.outputs['BSDF'], material_output.inputs['Surface'])

# Assign material to sphere
sphere.data.materials.append(material)

# Set viewport shading to show materials
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
