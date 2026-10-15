import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused datablocks
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
for material in list(bpy.data.materials):
    if material.users == 0:
        bpy.data.materials.remove(material)

# Dark ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.object
ground.name = "Dark Ground"

ground_material = bpy.data.materials.new("Dark Ground Material")
ground_material.use_nodes = True
ground_nodes = ground_material.node_tree.nodes
ground_links = ground_material.node_tree.links
ground_nodes.clear()

ground_output = ground_nodes.new("ShaderNodeOutputMaterial")
ground_shader = ground_nodes.new("ShaderNodeBsdfPrincipled")
ground_shader.inputs["Base Color"].default_value = (0.003, 0.006, 0.01, 1.0)
ground_shader.inputs["Roughness"].default_value = 0.82
ground_shader.inputs["Metallic"].default_value = 0.05
ground_links.new(ground_shader.outputs["BSDF"], ground_output.inputs["Surface"])
ground.data.materials.append(ground_material)

# Cyan neon torus hovering above the ground
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.13,
    major_segments=96,
    minor_segments=32,
    location=(0.0, 0.0, 1.2)
)
ring = bpy.context.object
ring.name = "Cyan Neon Ring"

# Smooth shading
for polygon in ring.data.polygons:
    polygon.use_smooth = True

# Emissive cyan material
emission_material = bpy.data.materials.new("Cyan Neon Emission")
emission_material.use_nodes = True
nodes = emission_material.node_tree.nodes
links = emission_material.node_tree.links
nodes.clear()

output_node = nodes.new("ShaderNodeOutputMaterial")
emission_node = nodes.new("ShaderNodeEmission")
emission_node.inputs["Color"].default_value = (0.0, 1.0, 1.0, 1.0)
emission_node.inputs["Strength"].default_value = 10.0
links.new(emission_node.outputs["Emission"], output_node.inputs["Surface"])

ring.data.materials.append(emission_material)

# Dark world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Dark World")
    bpy.context.scene.world = world

world.use_nodes = True
world_nodes = world.node_tree.nodes
background = world_nodes.get("Background")
if background:
    background.inputs["Color"].default_value = (0.001, 0.002, 0.004, 1.0)
    background.inputs["Strength"].default_value = 0.03
