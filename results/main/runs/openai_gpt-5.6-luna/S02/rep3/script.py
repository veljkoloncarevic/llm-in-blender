import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused datablocks created by the default scene
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)

# Create the floor
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Checkerboard Floor"

floor_material = bpy.data.materials.new("Black and White Checker Material")
floor_material.use_nodes = True

floor_nodes = floor_material.node_tree.nodes
floor_links = floor_material.node_tree.links
floor_nodes.clear()

floor_output = floor_nodes.new("ShaderNodeOutputMaterial")
floor_output.location = (500, 0)

floor_shader = floor_nodes.new("ShaderNodeBsdfPrincipled")
floor_shader.location = (220, 0)
floor_shader.inputs["Roughness"].default_value = 0.42

texture_coord = floor_nodes.new("ShaderNodeTexCoord")
texture_coord.location = (-500, 0)

checker = floor_nodes.new("ShaderNodeTexChecker")
checker.location = (-220, 0)
checker.name = "Black and White Checker Texture"
checker.label = "Black and White Checker Texture"
checker.inputs["Color1"].default_value = (0.0, 0.0, 0.0, 1.0)
checker.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
checker.inputs["Scale"].default_value = 8.0

floor_links.new(texture_coord.outputs["Generated"], checker.inputs["Vector"])
floor_links.new(checker.outputs["Color"], floor_shader.inputs["Base Color"])
floor_links.new(floor_shader.outputs["BSDF"], floor_output.inputs["Surface"])

floor.data.materials.append(floor_material)

# Create the glossy red cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
cube = bpy.context.object
cube.name = "Glossy Red Cube"

cube_material = bpy.data.materials.new("Glossy Red Material")
cube_material.use_nodes = True

cube_nodes = cube_material.node_tree.nodes
cube_shader = cube_nodes.get("Principled BSDF")
cube_shader.inputs["Base Color"].default_value = (0.65, 0.005, 0.01, 1.0)
cube_shader.inputs["Roughness"].default_value = 0.08
cube_shader.inputs["Metallic"].default_value = 0.05

cube.data.materials.append(cube_material)

# Add a subtle bevel for clean glossy highlights
bevel = cube.modifiers.new("Small Edge Bevel", "BEVEL")
bevel.width = 0.06
bevel.segments = 4
bevel.limit_method = 'ANGLE'

# Smooth the beveled cube while preserving crisp planar faces
for polygon in cube.data.polygons:
    polygon.use_smooth = True

cube.data.set_sharp_from_angle(angle=0.5)
