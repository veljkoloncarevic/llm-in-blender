import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create checkerboard floor
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Checkerboard Floor"

floor_material = bpy.data.materials.new("Checkerboard Floor Material")
floor_material.use_nodes = True

floor_nodes = floor_material.node_tree.nodes
floor_links = floor_material.node_tree.links
floor_nodes.clear()

floor_output = floor_nodes.new("ShaderNodeOutputMaterial")
floor_output.location = (420, 0)

floor_bsdf = floor_nodes.new("ShaderNodeBsdfPrincipled")
floor_bsdf.location = (120, 0)
floor_bsdf.inputs["Roughness"].default_value = 0.32

floor_texture = floor_nodes.new("ShaderNodeTexCoord")
floor_texture.location = (-620, 0)

checker = floor_nodes.new("ShaderNodeTexChecker")
checker.location = (-220, 0)
checker.name = "Black and White Checker Texture"
checker.inputs["Color1"].default_value = (0.0, 0.0, 0.0, 1.0)
checker.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
checker.inputs["Scale"].default_value = 8.0

floor_links.new(floor_texture.outputs["Generated"], checker.inputs["Vector"])
floor_links.new(checker.outputs["Color"], floor_bsdf.inputs["Base Color"])
floor_links.new(floor_bsdf.outputs["BSDF"], floor_output.inputs["Surface"])

floor.data.materials.append(floor_material)

# Create glossy red cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.object
cube.name = "Glossy Red Cube"

cube_material = bpy.data.materials.new("Glossy Red Material")
cube_material.use_nodes = True

cube_bsdf = cube_material.node_tree.nodes.get("Principled BSDF")
cube_bsdf.inputs["Base Color"].default_value = (0.8, 0.008, 0.01, 1.0)
cube_bsdf.inputs["Roughness"].default_value = 0.08
cube_bsdf.inputs["Metallic"].default_value = 0.15

if "Coat Weight" in cube_bsdf.inputs:
    cube_bsdf.inputs["Coat Weight"].default_value = 0.35
if "Coat Roughness" in cube_bsdf.inputs:
    cube_bsdf.inputs["Coat Roughness"].default_value = 0.04

cube.data.materials.append(cube_material)

# Slightly soften the cube edges while preserving its cube shape
bevel = cube.modifiers.new("Subtle Edge Bevel", "BEVEL")
bevel.width = 0.06
bevel.segments = 3

bpy.context.view_layer.objects.active = cube
cube.select_set(True)
