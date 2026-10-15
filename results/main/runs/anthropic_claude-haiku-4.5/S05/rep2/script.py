import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a torus (neon ring)
bpy.ops.mesh.primitive_torus_add(
    radius1=2.0,
    radius2=0.3,
    location=(0, 0, 1.5)
)
torus = bpy.context.active_object

# Create material for the torus
mat = bpy.data.materials.new(name="CyanNeon")
mat.use_nodes = True
mat.shadow_method = 'NONE'

# Clear default nodes
mat.node_tree.nodes.clear()

# Create shader nodes for emissive material
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Create emission shader
emission_node = nodes.new(type='ShaderNodeEmission')
emission_node.inputs['Strength'].default_value = 5.0

# Set emission color to cyan
emission_node.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0)

# Create output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')

# Connect nodes
links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

# Assign material to torus
torus.data.materials.append(mat)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(
    size=10.0,
    location=(0, 0, 0)
)
ground = bpy.context.active_object
ground.name = "GroundPlane"

# Create dark material for ground plane
ground_mat = bpy.data.materials.new(name="DarkGround")
ground_mat.use_nodes = True

# Set ground material to dark
ground_mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)
ground.data.materials.append(ground_mat)

# Set viewport shading to show emission
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
