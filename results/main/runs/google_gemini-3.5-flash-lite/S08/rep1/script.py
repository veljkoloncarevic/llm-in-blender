import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a flat wall (Plane rotated to stand vertically)
bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0, 0, 2))
wall = bpy.context.active_object
wall.name = "BrickWall"
wall.rotation_euler = (1.57079, 0, 0) # Rotate 90 degrees on X to make it vertical

# Ensure normals point outward nicely (though flat plane is fine)
bpy.ops.object.shade_smooth()

# Create a new material for procedural bricks
mat = bpy.data.materials.new(name="ProceduralBrickMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create necessary nodes
node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = (600, 0)

node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
node_principled.location = (300, 0)
node_principled.inputs['Roughness'].default_value = 0.5

node_brick = nodes.new(type='ShaderNodeTexBrick')
node_brick.location = (-300, 0)
# Configure brick texture properties
node_brick.inputs['Color1'].default_value = (0.2, 0.2, 0.2, 1.0) # Dark reddish-brown mortar base
node_brick.inputs['Color2'].default_value = (0.65, 0.25, 0.15, 1.0) # Terracotta brick color
node_brick.inputs['Mortar Size'].default_value = 0.02
node_brick.inputs['Brick Width'].default_value = 0.5
node_brick.inputs['Row Height'].default_value = 0.25

node_bump = nodes.new(type='ShaderNodeBump')
node_bump.location = (0, -200)
node_bump.inputs['Strength'].default_value = 0.4
node_bump.inputs['Distance'].default_value = 0.03

# Link nodes together
# 1. Base Color from Brick Texture to Principled BSDF
links.new(node_brick.outputs['Color'], node_principled.inputs['Base Color'])

# 2. Fac (mortar pattern mask) from Brick Texture to Bump Height
links.new(node_brick.outputs['Fac'], node_bump.inputs['Height'])

# 3. Normal from Bump node to Principled BSDF Normal
links.new(node_bump.outputs['Normal'], node_principled.inputs['Normal'])

# 4. Principled BSDF Shader to Material Output Surface
links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

# Assign material to the wall
if wall.data.materials:
    wall.data.materials[0] = mat
else:
    wall.data.materials.append(mat)
