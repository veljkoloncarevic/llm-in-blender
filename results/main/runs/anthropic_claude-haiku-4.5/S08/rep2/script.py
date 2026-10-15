import bpy
import bmesh
from mathutils import Vector

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a plane for the wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
wall = bpy.context.active_object
wall.name = "BrickWall"

# Add subdivision surface for better displacement detail
subdiv = wall.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv.levels = 3
subdiv.render_levels = 4

# Create a new material
mat = bpy.data.materials.new(name="BrickMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]

# Clear default links
mat.node_tree.links.clear()
mat.node_tree.nodes.clear()

# Create nodes
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Brick texture for color
brick_tex = nodes.new(type='ShaderNodeTexBrick')
brick_tex.inputs['Scale'].default_value = 15.0
brick_tex.inputs['Mortar Size'].default_value = 0.15

# Separate RGB to get mortar pattern (use Color output)
color_ramp = nodes.new(type='ShaderNodeValRamp')
color_ramp.color_ramp.elements[0].color = (0.2, 0.2, 0.2, 1.0)
color_ramp.color_ramp.elements[1].color = (0.8, 0.2, 0.2, 1.0)

# Bump node for surface detail
bump = nodes.new(type='ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.8
bump.inputs['Distance'].default_value = 0.05

# Principled BSDF shader
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Roughness'].default_value = 0.6

# Material output
mat_output = nodes.new(type='ShaderNodeOutputMaterial')

# Coordinate and mapping for better control
coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
mapping.inputs['Scale'].default_value = (1, 1, 1)

# Connect nodes
# Coordinates to brick texture
links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], brick_tex.inputs['Vector'])

# Brick color to principled
links.new(brick_tex.outputs['Color'], principled.inputs['Base Color'])

# Use Mortar output (which is the pattern) for bump
links.new(brick_tex.outputs['Mortar'], bump.inputs['Height'])

# Bump to normal
links.new(bump.outputs['Normal'], principled.inputs['Normal'])

# Principled to output
links.new(principled.outputs['BSDF'], mat_output.inputs['Surface'])

# Assign material to wall
wall.data.materials.append(mat)

# Add displacement modifier for more pronounced effect
displace = wall.modifiers.new(name="Displacement", type='DISPLACE')
displace.strength = 0.3

# Create texture for displacement
disp_tex = bpy.data.textures.new(name="BrickDisplace", type='CLOUDS')
disp_tex.cloud_type = 'COLOR'
disp_tex.noise_scale = 2.0
displace.texture = disp_tex

# Rotate wall to face camera better
wall.rotation_euler = (0, 0, 0)
wall.scale = (2, 2, 1)
