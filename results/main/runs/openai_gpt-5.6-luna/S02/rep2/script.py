import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create checkerboard floor
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Checkerboard Floor"

floor_material = bpy.data.materials.new("Black and White Checker Material")
floor_material.use_nodes = True

nodes = floor_material.node_tree.nodes
links = floor_material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.location = (400, 0)

principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.location = (150, 0)
principled.inputs["Roughness"].default_value = 0.38

checker = nodes.new("ShaderNodeTexChecker")
checker.location = (-180, 0)
checker.inputs["Color1"].default_value = (0.0, 0.0, 0.0, 1.0)
checker.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
checker.inputs["Scale"].default_value = 8.0

links.new(checker.outputs["Color"], principled.inputs["Base Color"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

floor.data.materials.append(floor_material)

# Create glossy red cube sitting on the floor
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
cube = bpy.context.object
cube.name = "Glossy Red Cube"

cube_material = bpy.data.materials.new("Glossy Red Material")
cube_material.use_nodes = True

cube_principled = cube_material.node_tree.nodes.get("Principled BSDF")
cube_principled.inputs["Base Color"].default_value = (0.8, 0.015, 0.02, 1.0)
cube_principled.inputs["Roughness"].default_value = 0.08
cube_principled.inputs["Metallic"].default_value = 0.0

cube.data.materials.append(cube_material)

# Slight bevel for attractive glossy highlights
bevel = cube.modifiers.new("Small Edge Bevel", "BEVEL")
bevel.width = 0.06
bevel.segments = 3

for polygon in cube.data.polygons:
    polygon.use_smooth = True
