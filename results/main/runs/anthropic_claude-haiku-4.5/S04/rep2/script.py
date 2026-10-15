import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV Sphere (glass sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = "GlassSphere"

# Create material for the glass sphere
glass_material = bpy.data.materials.new(name="GlassMaterial")
glass_material.use_nodes = True
glass_material.shadow_method = 'HASHED'

# Clear default nodes
glass_material.node_tree.nodes.clear()

# Add Principled BSDF node
principled = glass_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Transmission'].default_value = 1.0
principled.inputs['Roughness'].default_value = 0.01
principled.inputs['IOR'].default_value = 1.45

# Add Material Output node
output = glass_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

# Connect Principled BSDF to Material Output
glass_material.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to sphere
sphere.data.materials.append(glass_material)

# Create a blue ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "GroundPlane"

# Create blue material for the plane
blue_material = bpy.data.materials.new(name="BlueMaterial")
blue_material.use_nodes = True

# Clear default nodes
blue_material.node_tree.nodes.clear()

# Add Principled BSDF node for blue color
principled_blue = blue_material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
principled_blue.inputs['Base Color'].default_value = (0.0, 0.3, 0.8, 1.0)

# Add Material Output node
output_blue = blue_material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

# Connect Principled BSDF to Material Output
blue_material.node_tree.links.new(principled_blue.outputs['BSDF'], output_blue.inputs['Surface'])

# Assign material to plane
plane.data.materials.append(blue_material)
