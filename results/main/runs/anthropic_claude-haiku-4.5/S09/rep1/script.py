import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
sphere = bpy.context.active_object

# Create a new material
material = bpy.data.materials.new(name="Deep_Red_Car_Paint")
material.use_nodes = True

# Clear default nodes
material.node_tree.nodes.clear()

# Create nodes
nodes = material.node_tree.nodes
links = material.node_tree.links

# Create Principled BSDF node
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (0.5, 0.0, 0.0, 1.0)  # Deep red
principled.inputs['Metallic'].default_value = 0.5
principled.inputs['Roughness'].default_value = 0.2
principled.inputs['Coat Weight'].default_value = 0.85  # Strong clear coat
principled.inputs['Coat Roughness'].default_value = 0.1

# Create Material Output node
material_output = nodes.new(type='ShaderNodeOutputMaterial')

# Connect Principled BSDF to Material Output
links.new(principled.outputs['BSDF'], material_output.inputs['Surface'])

# Assign material to sphere
sphere.data.materials.append(material)
