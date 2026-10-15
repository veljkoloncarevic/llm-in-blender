import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a plane to serve as the wall
bpy.ops.mesh.primitive_plane_add(size=4.0, enter_editmode=False, location=(0, 0, 0))
wall_obj = bpy.active_object
wall_obj.name = "BrickWall"

# Rotate wall to stand vertically (facing along Y)
wall_obj.rotation_euler = (1.57079, 0, 0)

# Apply scale to ensure proper texture mapping
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Create a new material for the procedural brick
mat = bpy.data.materials.new(name="ProceduralBrickMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add Texture Coordinate and Mapping for fine control over scale/rotation
node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
node_tex_coord.location = (-900, 200)

node_mapping = nodes.new(type='ShaderNodeMapping')
node_mapping.location = (-700, 200)
# Adjust mapping scale to fit the wall nicely
node_mapping.inputs['Scale'].default_value = (2.0, 2.0, 2.0)

# Add Brick Texture Node
node_brick = nodes.new(type='ShaderNodeTexBrick')
node_brick.location = (-450, 200)
# Configure brick properties for aesthetic appeal
node_brick.inputs['Color1'].default_value = (0.65, 0.25, 0.15, 1.0)  # Terracotta/Red Brick
node_brick.inputs['Color2'].default_value = (0.50, 0.20, 0.12, 1.0)  # Darker Red Variant
node_brick.inputs['Mortar'].default_value = (0.8, 0.8, 0.8, 1.0)    # Light gray mortar
node_brick.inputs['Scale'].default_value = 8.0
node_brick.inputs['Mortar Size'].default_value = 0.02
node_brick.inputs['Row Height'].default_value = 0.5
node_brick.inputs['Offset'].default_value = 0.5

# Add Bump Node to drive the surface relief using the mortar pattern
node_bump = nodes.new(type='ShaderNodeBump')
node_bump.location = (-150, -100)
node_bump.inputs['Strength'].default_value = 0.8
node_bump.inputs['Distance'].default_value = 0.03

# Add Principled BSDF Shader
node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
node_principled.location = (150, 200)
# Adjust roughness for a realistic matte/clay brick look
node_principled.inputs['Roughness'].default_value = 0.65

# Add Material Output
node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = (450, 200)

# Link nodes together
# Texture coordinates -> Mapping -> Brick Texture
links.new(node_tex_coord.outputs['UV'], node_mapping.inputs['Vector'])
links.new(node_mapping.outputs['Vector'], node_brick.inputs['Vector'])

# Brick Color -> Principled Base Color
links.new(node_brick.outputs['Color'], node_principled.inputs['Base Color'])

# Brick Fac (Mortar pattern) -> Bump Height -> Principled Normal
links.new(node_brick.outputs['Fac'], node_bump.inputs['Height'])
links.new(node_bump.outputs['Normal'], node_principled.inputs['Normal'])

# Principled Shader -> Material Output
links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

# Assign material to the wall object
if wall_obj.data.materials:
    wall_obj.data.materials[0] = mat
else:
    wall_obj.data.materials.append(mat)
