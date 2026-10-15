import bpy
import bmesh

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
    pass

# Create the wall mesh
mesh = bpy.data.meshes.new("WallMesh")
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2.0)
bm.to_mesh(mesh)
bm.free()

wall = bpy.data.objects.new("Brick Wall", mesh)
bpy.context.collection.objects.link(wall)

# Shape the wall
wall.dimensions = (10.0, 0.35, 6.0)
wall.location = (0.0, 0.0, 3.0)
bpy.context.view_layer.objects.active = wall
wall.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Slightly soften the wall edges
bevel = wall.modifiers.new("Soft Wall Edges", 'BEVEL')
bevel.width = 0.04
bevel.segments = 3

# Create procedural brick material
material = bpy.data.materials.new("Procedural Brick Material")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (700, 0)

shader = nodes.new("ShaderNodeBsdfPrincipled")
shader.name = "Brick Principled Shader"
shader.location = (420, 0)
shader.inputs["Roughness"].default_value = 0.82

texcoord = nodes.new("ShaderNodeTexCoord")
texcoord.name = "Generated Coordinates"
texcoord.location = (-900, 100)

separate = nodes.new("ShaderNodeSeparateXYZ")
separate.name = "Wall Plane Coordinates"
separate.location = (-700, 100)

combine = nodes.new("ShaderNodeCombineXYZ")
combine.name = "Brick Coordinate Mapping"
combine.location = (-500, 100)
combine.inputs["Z"].default_value = 0.0

brick = nodes.new("ShaderNodeTexBrick")
brick.name = "Brick Texture"
brick.label = "Procedural Brick and Mortar"
brick.location = (-250, 100)

brick.offset = 0.5
brick.offset_frequency = 2
brick.squash = 1.0
brick.squash_frequency = 2
brick.inputs["Color1"].default_value = (0.42, 0.075, 0.035, 1.0)
brick.inputs["Color2"].default_value = (0.72, 0.20, 0.08, 1.0)
brick.inputs["Mortar"].default_value = (0.055, 0.045, 0.035, 1.0)
brick.inputs["Scale"].default_value = 5.2
brick.inputs["Mortar Size"].default_value = 0.045
brick.inputs["Mortar Smooth"].default_value = 0.012
brick.inputs["Bias"].default_value = 0.0
brick.inputs["Brick Width"].default_value = 0.72
brick.inputs["Row Height"].default_value = 0.27

bump = nodes.new("ShaderNodeBump")
bump.name = "Mortar Bump"
bump.label = "Mortar Pattern Bump"
bump.location = (170, -170)
bump.inputs["Strength"].default_value = 0.42
bump.inputs["Distance"].default_value = 0.075

links.new(texcoord.outputs["Generated"], separate.inputs["Vector"])
links.new(separate.outputs["X"], combine.inputs["X"])
links.new(separate.outputs["Z"], combine.inputs["Y"])
links.new(combine.outputs["Vector"], brick.inputs["Vector"])

# Brick colour drives the surface colour
links.new(brick.outputs["Color"], shader.inputs["Base Color"])

# Brick texture factor contains the brick/mortar pattern and drives bump relief
links.new(brick.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], shader.inputs["Normal"])

links.new(shader.outputs["BSDF"], output.inputs["Surface"])

wall.data.materials.append(material)

# Set a useful viewport display colour
material.diffuse_color = (0.55, 0.12, 0.045, 1.0)
