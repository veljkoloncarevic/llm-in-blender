import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a vertical wall plane (4m wide, 3m tall)
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
wall = bpy.context.active_object
wall.name = "Wall"

# Scale plane to wall dimensions, then rotate it upright
wall.scale = (2.0, 1.5, 1.0)  # 4m x 3m
wall.rotation_euler = (math.radians(90), 0, 0)

# Apply transforms so the object has real dimensions and clean transform
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Create procedural brick material
mat = bpy.data.materials.new(name="BrickWall")
mat.use_nodes = True
ntree = mat.node_tree
nodes = ntree.nodes
links = ntree.links

# Clear default nodes
nodes.clear()

# Create all necessary nodes
tex_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
brick = nodes.new(type='ShaderNodeTexBrick')
math_inv = nodes.new(type='ShaderNodeMath')
bump = nodes.new(type='ShaderNodeBump')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
output = nodes.new(type='ShaderNodeOutputMaterial')

# Arrange nodes in a readable layout
tex_coord.location = (-1000, 0)
mapping.location = (-800, 0)
brick.location = (-600, 0)
math_inv.location = (-350, -200)
bump.location = (-150, -200)
principled.location = (0, 0)
output.location = (250, 0)

# Configure math node: invert Fac so mortar is recessed
math_inv.operation = 'SUBTRACT'
math_inv.inputs[0].default_value = 1.0

# Configure Bump
bump.inputs['Distance'].default_value = 0.02

# Configure Brick Texture parameters
brick.inputs['Scale'].default_value = 4.0
brick.inputs['Brick Width'].default_value = 0.5
brick.inputs['Row Height'].default_value = 0.333
brick.inputs['Mortar Size'].default_value = 0.02
brick.inputs['Mortar Smooth'].default_value = 0.1
brick.inputs['Color1'].default_value = (0.6, 0.15, 0.1, 1.0)   # dark red brick
brick.inputs['Color2'].default_value = (0.8, 0.25, 0.15, 1.0)  # lighter red brick
brick.inputs['Mortar'].default_value = (0.8, 0.8, 0.8, 1.0)    # grey mortar

# Connect nodes
links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
links.new(brick.outputs['Color'], principled.inputs['Base Color'])
links.new(brick.outputs['Fac'], math_inv.inputs[1])
links.new(math_inv.outputs[0], bump.inputs['Height'])
links.new(bump.outputs['Normal'], principled.inputs['Normal'])
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to the wall
if wall.data.materials:
    wall.data.materials[0] = mat
else:
    wall.data.materials.append(mat)
