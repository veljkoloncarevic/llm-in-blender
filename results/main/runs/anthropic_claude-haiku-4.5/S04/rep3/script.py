import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground_plane = bpy.context.active_object
ground_plane.name = "GroundPlane"

# Create blue material for ground plane
blue_material = bpy.data.materials.new(name="BlueMaterial")
blue_material.use_nodes = True
blue_material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.0, 1.0, 1.0)
ground_plane.data.materials.append(blue_material)

# Create a glass sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, location=(0, 0, 1.5))
sphere = bpy.context.active_object
sphere.name = "GlassSphere"

# Create clear glass material
glass_material = bpy.data.materials.new(name="ClearGlass")
glass_material.use_nodes = True
nodes = glass_material.node_tree.nodes
links = glass_material.node_tree.links

# Clear default nodes
nodes.clear()

# Create Principled BSDF node
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs["Transmission"].default_value = 1.0  # Full transmission
principled.inputs["Roughness"].default_value = 0.01    # Near 0 roughness
principled.inputs["IOR"].default_value = 1.45          # IOR for glass

# Create Material Output node
output = nodes.new(type='ShaderNodeOutputMaterial')

# Connect Principled BSDF to Material Output
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

# Add material to sphere
sphere.data.materials.append(glass_material)
