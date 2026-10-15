import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a torus (neon ring)
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.3,
    location=(0, 0, 1.5)
)
torus = bpy.context.active_object

# Create a material for the glowing cyan neon ring
neon_material = bpy.data.materials.new(name="CyanNeon")
neon_material.use_nodes = True
neon_material.shadow_method = 'NONE'

# Clear default nodes
neon_material.node_tree.nodes.clear()

# Create shader nodes for emissive material
nodes = neon_material.node_tree.nodes
links = neon_material.node_tree.links

# Add Principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (0.0, 1.0, 1.0, 1.0)  # Cyan
principled.inputs['Emission'].default_value = (0.0, 1.0, 1.0, 1.0)  # Cyan emission
principled.inputs['Emission Strength'].default_value = 5.0

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to torus
torus.data.materials.append(neon_material)

# Create a dark ground plane
bpy.ops.mesh.primitive_plane_add(
    size=10.0,
    location=(0, 0, 0)
)
ground = bpy.context.active_object

# Create a dark material for the ground plane
ground_material = bpy.data.materials.new(name="DarkGround")
ground_material.use_nodes = True

# Clear default nodes
ground_material.node_tree.nodes.clear()

# Create shader nodes for dark material
ground_nodes = ground_material.node_tree.nodes
ground_links = ground_material.node_tree.links

# Add Principled BSDF
ground_principled = ground_nodes.new(type='ShaderNodeBsdfPrincipled')
ground_principled.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)  # Very dark gray
ground_principled.inputs['Roughness'].default_value = 0.8

# Add Material Output
ground_output = ground_nodes.new(type='ShaderNodeOutputMaterial')
ground_links.new(ground_principled.outputs['BSDF'], ground_output.inputs['Surface'])

# Assign material to ground plane
ground.data.materials.append(ground_material)
