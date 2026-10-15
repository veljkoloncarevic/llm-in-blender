import bpy

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a wall (scaled cube acting as a thin wall)
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1))
wall = bpy.active_object
wall.name = "Procedural_Brick_Wall"
wall.scale = (0.2, 4.0, 2.0)
bpy.ops.object.transform_apply(scale=True)

# Create a new material with Nodes
material = bpy.data.materials.new(name="BrickWallMaterial")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create Material Output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (600, 0)

# Create Principled BSDF node
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (300, 0)
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Create Texture Coordinate and Mapping nodes for procedural placement
tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
tex_coord_node.location = (-900, 0)

mapping_node = nodes.new(type='ShaderNodeMapping')
mapping_node.location = (-700, 0)
# Rotate to fit vertical wall orientation if necessary, and scale
mapping_node.inputs['Rotation'].default_value[0] = 1.57079  # 90 degrees on X
mapping_node.inputs['Scale'].default_value[1] = 2.0
mapping_node.inputs['Scale'].default_value[2] = 2.0
links.new(tex_coord_node.outputs['Object'], mapping_node.inputs['Vector'])

# Create Brick Texture node
brick_node = nodes.new(type='ShaderNodeTexBrick')
brick_node.location = (-400, 0)

# Configure Brick Texture properties for a classic look
brick_node.inputs['Color1'].default_value = (0.65, 0.25, 0.15, 1.0)  # Reddish-brown brick
brick_node.inputs['Color2'].default_value = (0.50, 0.18, 0.10, 1.0)  # Darker variant
brick_node.inputs['Mortar'].default_value = (0.8, 0.8, 0.8, 1.0)    # Light gray mortar
brick_node.inputs['Scale'].default_value = 5.0
brick_node.inputs['Mortar Size'].default_value = 0.02
brick_node.inputs['Mortar Smooth'].default_value = 0.01
brick_node.inputs['Bias'].default_value = 0.0
brick_node.inputs['Brick Width'].default_value = 0.5
brick_node.inputs['Row Height'].default_value = 0.25

links.new(mapping_node.outputs['Vector'], brick_node.inputs['Vector'])

# Create Bump node driven by the mortar pattern (Fac output of Brick Texture)
bump_node = nodes.new(type='ShaderNodeBump')
bump_node.location = (0, -200)
bump_node.inputs['Strength'].default_value = 0.5
bump_node.inputs['Distance'].default_value = 0.03

links.new(brick_node.outputs['Fac'], bump_node.inputs['Height'])
links.new(bump_node.outputs['Normal'], principled_node.inputs['Normal'])

# Connect Brick Color to Principled Base Color
links.new(brick_node.outputs['Color'], principled_node.inputs['Base Color'])

# Set Roughness for a slightly weathered look
principled_node.inputs['Roughness'].default_value = 0.6

# Assign material to the wall object
if wall.data.materials:
    wall.data.materials[0] = material
else:
    wall.data.materials.append(material)

# Set shading to smooth for the base mesh
for polygon in wall.data.polygons:
    polygon.use_smooth = True
