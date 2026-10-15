import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a torus (neon ring)
bpy.ops.mesh.primitive_torus_add(
    radius1=2.0,  # Major radius
    radius2=0.3,  # Minor radius (thickness)
    location=(0, 0, 1.5)
)
torus = bpy.context.active_object
torus.name = "NeonRing"

# Create emissive cyan material for the torus
mat_neon = bpy.data.materials.new(name="CyanNeon")
mat_neon.use_nodes = True
mat_neon.shadow_method = 'NONE'

# Clear default nodes
mat_neon.node_tree.nodes.clear()

# Create shader nodes for emissive material
nodes = mat_neon.node_tree.nodes
links = mat_neon.node_tree.links

# Add Principled BSDF
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (0.0, 1.0, 1.0, 1.0)  # Cyan
principled.inputs['Emission'].default_value = (0.0, 1.0, 1.0, 1.0)  # Cyan emission
principled.inputs['Emission Strength'].default_value = 5.0  # Emission strength

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')

# Connect Principled to Material Output
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to torus
torus.data.materials.append(mat_neon)

# Create dark ground plane
bpy.ops.mesh.primitive_plane_add(
    size=10.0,
    location=(0, 0, -0.5)
)
ground = bpy.context.active_object
ground.name = "GroundPlane"

# Create dark material for ground plane
mat_ground = bpy.data.materials.new(name="DarkGround")
mat_ground.use_nodes = True

# Clear default nodes
mat_ground.node_tree.nodes.clear()

# Create shader nodes for dark material
nodes_ground = mat_ground.node_tree.nodes
links_ground = mat_ground.node_tree.links

# Add Principled BSDF for ground
principled_ground = nodes_ground.new(type='ShaderNodeBsdfPrincipled')
principled_ground.inputs['Base Color'].default_value = (0.05, 0.05, 0.05, 1.0)  # Very dark gray
principled_ground.inputs['Roughness'].default_value = 0.8

# Add Material Output
output_ground = nodes_ground.new(type='ShaderNodeOutputMaterial')

# Connect Principled to Material Output
links_ground.new(principled_ground.outputs['BSDF'], output_ground.inputs['Surface'])

# Assign material to ground plane
ground.data.materials.append(mat_ground)
