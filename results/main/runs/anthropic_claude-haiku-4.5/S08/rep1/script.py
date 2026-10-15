import bpy
import bmesh
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a plane for the wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
wall = bpy.context.active_object
wall.name = "Wall"

# Scale it to make it more wall-like
wall.scale = (5, 3, 1)
bpy.context.view_layer.objects.active = wall
bpy.ops.object.transform_apply(scale=True)

# Create a new material
mat = bpy.data.materials.new(name="BrickMaterial")
mat.use_nodes = True
mat.shadow_method = 'HASHED'

# Clear default nodes
nodes = mat.node_tree.nodes
nodes.clear()
links = mat.node_tree.links

# Create nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
brick_texture = nodes.new(type='ShaderNodeTexBrick')
bump_node = nodes.new(type='ShaderNodeBump')
color_ramp = nodes.new(type='ShaderNodeValRamp')

# Configure Brick Texture node for color
brick_texture.inputs['Scale'].default_value = 15.0
brick_texture.inputs['Mortar Size'].default_value = 0.02
brick_texture.inputs['Mortar Smooth'].default_value = 0.1
brick_texture.inputs['Bias'].default_value = 0.0
brick_texture.inputs['Brick Width'].default_value = 0.75
brick_texture.inputs['Row Height'].default_value = 0.3

# Set brick and mortar colors
brick_texture.inputs['Color1'].default_value = (0.6, 0.3, 0.1, 1.0)  # Brick color (brown)
brick_texture.inputs['Color2'].default_value = (0.7, 0.65, 0.6, 1.0)  # Mortar color (light gray)

# Configure Color Ramp to extract mortar pattern from Brick texture
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[1].position = 0.5

# Configure Bump node
bump_node.inputs['Strength'].default_value = 0.5
bump_node.inputs['Distance'].default_value = 1.0

# Configure BSDF
bsdf_node.inputs['Roughness'].default_value = 0.8

# Create links
# Brick texture color to BSDF
links.new(brick_texture.outputs['Color'], bsdf_node.inputs['Base Color'])

# Brick texture Fac (mortar pattern) to Color Ramp
links.new(brick_texture.outputs['Fac'], color_ramp.inputs['Fac'])

# Color Ramp output to Bump node Height
links.new(color_ramp.outputs['Color'], bump_node.inputs['Height'])

# Bump node to BSDF Normal
links.new(bump_node.outputs['Normal'], bsdf_node.inputs['Normal'])

# BSDF to output
links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

# Add material to the wall
if wall.data.materials:
    wall.data.materials[0] = mat
else:
    wall.data.materials.append(mat)

# Add a subdivision surface modifier for better geometry
subsurf = wall.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3

# Set viewport shading to Material Preview or Rendered to see the material
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'

print("Brick wall with procedural material created successfully!")
