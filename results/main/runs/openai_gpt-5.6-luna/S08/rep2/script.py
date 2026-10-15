import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a thin wall
bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 2.5))
wall = bpy.context.object
wall.name = "Brick Wall"
wall.dimensions = (8.0, 0.25, 5.0)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Slightly soften the wall edges
bevel = wall.modifiers.new(name="Soft Edges", type='BEVEL')
bevel.width = 0.035
bevel.segments = 2

# Create procedural brick material
material = bpy.data.materials.new(name="Procedural Brick Material")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (650, 0)

principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.name = "Brick Principled BSDF"
principled.location = (350, 0)
principled.inputs["Roughness"].default_value = 0.82

texcoord = nodes.new("ShaderNodeTexCoord")
texcoord.name = "Wall Coordinates"
texcoord.location = (-850, 0)

separate = nodes.new("ShaderNodeSeparateXYZ")
separate.name = "Orient Coordinates"
separate.location = (-650, 0)

combine = nodes.new("ShaderNodeCombineXYZ")
combine.name = "Wall Surface Coordinates"
combine.location = (-450, 0)

brick = nodes.new("ShaderNodeTexBrick")
brick.name = "Procedural Brick Texture"
brick.label = "Brick Colour and Mortar Pattern"
brick.location = (-150, 100)

brick.offset = 0.5
brick.offset_frequency = 2
brick.squash = 1.0
brick.squash_frequency = 2

brick.inputs["Color1"].default_value = (0.48, 0.075, 0.035, 1.0)
brick.inputs["Color2"].default_value = (0.22, 0.025, 0.012, 1.0)
brick.inputs["Mortar"].default_value = (0.055, 0.045, 0.035, 1.0)
brick.inputs["Scale"].default_value = 7.0
brick.inputs["Mortar Size"].default_value = 0.055
brick.inputs["Mortar Smooth"].default_value = 0.015
brick.inputs["Bias"].default_value = 0.0
brick.inputs["Brick Width"].default_value = 0.78
brick.inputs["Row Height"].default_value = 0.32

bump = nodes.new("ShaderNodeBump")
bump.name = "Mortar Bump"
bump.label = "Mortar Pattern Bump"
bump.location = (100, -180)
bump.inputs["Strength"].default_value = 0.32
bump.inputs["Distance"].default_value = 0.08
bump.invert = True

# Generated coordinates are remapped so the brick texture runs across X/Z
# on the front and back faces of the wall.
links.new(texcoord.outputs["Generated"], separate.inputs["Vector"])
links.new(separate.outputs["X"], combine.inputs["X"])
links.new(separate.outputs["Z"], combine.inputs["Y"])
links.new(separate.outputs["Y"], combine.inputs["Z"])
links.new(combine.outputs["Vector"], brick.inputs["Vector"])

# Brick colour drives the material colour
links.new(brick.outputs["Color"], principled.inputs["Base Color"])

# Brick texture factor, containing the mortar pattern, drives surface relief
links.new(brick.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])

links.new(principled.outputs["BSDF"], output.inputs["Surface"])

wall.data.materials.append(material)

# Set a useful viewport display colour
material.diffuse_color = (0.48, 0.075, 0.035, 1.0)
