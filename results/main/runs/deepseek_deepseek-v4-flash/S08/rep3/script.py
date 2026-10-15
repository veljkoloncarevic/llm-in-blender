import bpy

# Remove all existing objects
if bpy.context.scene.objects:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

# Create a thin box wall
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
wall = bpy.context.object
wall.name = "Wall"
wall.dimensions = (4.0, 0.2, 3.0)

# Create procedural brick material
mat = bpy.data.materials.new(name="BrickMaterial")
mat.use_nodes = True
ntree = mat.node_tree
nodes = ntree.nodes
links = ntree.links

# Clear default nodes
nodes.clear()

# Create node elements
out = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
brick = nodes.new(type='ShaderNodeTexBrick')
bump = nodes.new(type='ShaderNodeBump')
tex_coord = nodes.new(type='ShaderNodeTexCoord')

# Layout
out.location = (300, 0)
principled.location = (50, 0)
bump.location = (-200, 100)
brick.location = (-450, 0)
tex_coord.location = (-700, -100)

# Brick texture settings
brick.brick_color = (0.58, 0.21, 0.12, 1.0)
brick.mortar_color = (0.82, 0.82, 0.82, 1.0)
brick.scale = 4.0
brick.mortar_size = 0.025
brick.mortar_smooth = 0.1
brick.bias = 0.0
brick.brick_width = 0.5
brick.row_height = 0.25
brick.offset = 0.5
brick.offset_frequency = 2
brick.squash = 1.0
brick.squash_frequency = 1

# Bump settings
bump.strength = 0.05
bump.invert = False

# Connections
links.new(tex_coord.outputs['Generated'], brick.inputs['Vector'])
links.new(brick.outputs['Color'], principled.inputs['Base Color'])
links.new(brick.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], principled.inputs['Normal'])
links.new(principled.outputs['BSDF'], out.inputs['Surface'])

# Assign material to the wall
if wall.data.materials:
    wall.data.materials[0] = mat
else:
    wall.data.materials.append(mat)
