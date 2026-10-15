import bpy
import math

# Make sure we're in Object Mode and remove all existing objects
if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a vertical wall from a plane
bpy.ops.mesh.primitive_plane_add(size=4, enter_editmode=False, align='WORLD', location=(0, 0, 0))
wall = bpy.context.active_object
wall.name = "Wall"
wall.rotation_euler = (math.radians(90), 0, 0)
wall.scale = (2.0, 1.5, 1.0)  # 8 units wide, 6 units tall

# Create the procedural brick material
mat = bpy.data.materials.new(name="BrickMaterial")
mat.use_nodes = True
ntree = mat.node_tree
nodes = ntree.nodes
links = ntree.links

# Clear default shader nodes
nodes.clear()

# Add required nodes
tex_coord = nodes.new(type='ShaderNodeTexCoord')
brick = nodes.new(type='ShaderNodeTexBrick')
bump = nodes.new(type='ShaderNodeBump')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Arrange nodes in the editor
tex_coord.location = (-800, 0)
brick.location = (-500, 0)
bump.location = (-200, -250)
principled.location = (-200, 200)
output.location = (100, 0)

# Configure the brick texture
brick.color1 = (0.45, 0.15, 0.08)   # Main brick colour
brick.color2 = (0.38, 0.12, 0.06)   # Brick colour variation
brick.mortar = (0.85, 0.83, 0.80)   # Mortar colour
brick.scale = 2.0
brick.mortar_size = 0.02
brick.mortar_smooth = 0.1
brick.bias = 0.0
brick.brick_width = 0.6
brick.row_height = 0.3

# Configure the bump node
bump.inputs['Strength'].default_value = 1.0
bump.inputs['Distance'].default_value = 0.05

# Build node connections
links.new(tex_coord.outputs['Object'], brick.inputs['Vector'])
links.new(brick.outputs['Color'], principled.inputs['Base Color'])
links.new(brick.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], principled.inputs['Normal'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign the material to the wall
wall.data.materials.append(mat)
