import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a thin wall
bpy.ops.mesh.primitive_cube_add(
    location=(0.0, 0.0, 2.5),
    scale=(4.0, 0.12, 2.5)
)
wall = bpy.context.object
wall.name = "Procedural Brick Wall"

# Apply scale for consistent geometry and shading
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Slightly soften the wall edges
bevel = wall.modifiers.new(name="Subtle Edge Bevel", type='BEVEL')
bevel.width = 0.025
bevel.segments = 2

# Create procedural brick material
material = bpy.data.materials.new(name="Procedural Brick Material")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (700, 0)

principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.name = "Brick Principled Shader"
principled.location = (420, 0)
principled.inputs["Roughness"].default_value = 0.82
principled.inputs["Specular IOR Level"].default_value = 0.25

texcoord = nodes.new("ShaderNodeTexCoord")
texcoord.name = "Wall Coordinates"
texcoord.location = (-900, 0)

separate = nodes.new("ShaderNodeSeparateXYZ")
separate.name = "Separate Wall Coordinates"
separate.location = (-700, 0)

combine = nodes.new("ShaderNodeCombineXYZ")
combine.name = "Flatten Coordinates To Wall Plane"
combine.location = (-500, 0)
combine.inputs["Z"].default_value = 0.0

brick = nodes.new("ShaderNodeTexBrick")
brick.name = "Procedural Brick Texture"
brick.label = "Brick Colour and Mortar Pattern"
brick.location = (-220, 0)

brick.offset = 0.5
brick.offset_frequency = 2
brick.squash = 1.0
brick.squash_frequency = 2

brick.inputs["Color1"].default_value = (0.48, 0.075, 0.035, 1.0)
brick.inputs["Color2"].default_value = (0.22, 0.025, 0.012, 1.0)
brick.inputs["Mortar"].default_value = (0.055, 0.045, 0.035, 1.0)
brick.inputs["Scale"].default_value = 8.0
brick.inputs["Mortar Size"].default_value = 0.045
brick.inputs["Mortar Smooth"].default_value = 0.012
brick.inputs["Bias"].default_value = 0.0
brick.inputs["Brick Width"].default_value = 0.72
brick.inputs["Row Height"].default_value = 0.28

bump = nodes.new("ShaderNodeBump")
bump.name = "Brick Mortar Bump"
bump.label = "Mortar Relief"
bump.location = (170, -220)
bump.inputs["Strength"].default_value = 0.38
bump.inputs["Distance"].default_value = 0.08
bump.invert = True

# Use Generated coordinates, remapping X and Z onto the Brick Texture's X/Y plane
links.new(texcoord.outputs["Generated"], separate.inputs["Vector"])
links.new(separate.outputs["X"], combine.inputs["X"])
links.new(separate.outputs["Z"], combine.inputs["Y"])
links.new(combine.outputs["Vector"], brick.inputs["Vector"])

# Brick colour drives the shader colour
links.new(brick.outputs["Color"], principled.inputs["Base Color"])

# Brick factor drives the mortar/brick bump pattern
links.new(brick.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])

links.new(principled.outputs["BSDF"], output.inputs["Surface"])

# Assign material
wall.data.materials.append(material)

# Set a useful viewport display colour
material.diffuse_color = (0.38, 0.055, 0.02, 1.0)

# Ensure the wall is selected and active
bpy.context.view_layer.objects.active = wall
wall.select_set(True)
