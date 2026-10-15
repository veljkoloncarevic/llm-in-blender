import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a plane for the wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
wall = bpy.context.active_object
wall.name = "BrickWall"

# Scale the plane to make it more wall-like
wall.scale = (5, 8, 1)

# Add a subdivision surface modifier for better detail
subdiv = wall.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv.levels = 2
subdiv.render_levels = 3

# Create a new material
material = bpy.data.materials.new(name="BrickMaterial")
material.use_nodes = True
material.diffuse_color = (0.8, 0.8, 0.8, 1.0)

# Clear default nodes
nodes = material.node_tree.nodes
nodes.clear()

# Create shader nodes
links = material.node_tree.links

# Main shader
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Roughness'].default_value = 0.7

# Output node
output = nodes.new(type='ShaderNodeOutputMaterial')

# Brick Texture for color
brick_tex = nodes.new(type='ShaderNodeTexBrick')
brick_tex.inputs['Scale'].default_value = 15.0
brick_tex.inputs['Mortar Thickness'].default_value = 0.15
brick_tex.inputs['Bias'].default_value = 0.0
brick_tex.inputs['Brick Width'].default_value = 0.75
brick_tex.inputs['Row Height'].default_value = 0.5

# Set brick colors
brick_tex.inputs['Color1'].default_value = (0.6, 0.3, 0.2, 1.0)  # Brick red
brick_tex.inputs['Color2'].default_value = (0.65, 0.35, 0.25, 1.0)  # Brick variation
brick_tex.inputs['Mortar'].default_value = (0.75, 0.75, 0.75, 1.0)  # Light gray mortar

# Bump node driven by mortar pattern
bump = nodes.new(type='ShaderNodeBump')
bump.inputs['Strength'].default_value = 0.8
bump.inputs['Distance'].default_value = 1.0

# Separate RGB to extract mortar pattern (use the color output as mask)
color_ramp = nodes.new(type='ShaderNodeValRamp')
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[1].position = 0.3

# Displacement node for additional detail
displacement = nodes.new(type='ShaderNodeDisplacement')
displacement.inputs['Strength'].default_value = 0.1
displacement.inputs['Midlevel'].default_value = 0.5

# Connect nodes
# Brick texture color to BSDF
links.new(brick_tex.outputs['Color'], bsdf.inputs['Base Color'])

# Brick texture for bump mapping (use the color as displacement driver)
links.new(brick_tex.outputs['Color'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Connect to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Apply material to wall
wall.data.materials.append(material)

# Add UV mapping for proper texture coordinates
uv_layer = wall.data.uv_layers.new(name="UVMap")

# Map the material to use generated coordinates
for node in nodes:
    if node.type == 'TEX_BRICK':
        # Add texture coordinate node
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        links.new(tex_coord.outputs['Generated'], node.inputs['Vector'])

bpy.context.view_layer.objects.active = wall
wall.select_set(True)
