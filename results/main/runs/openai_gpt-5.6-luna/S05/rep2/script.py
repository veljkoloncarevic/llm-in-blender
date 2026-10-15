import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Dark ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.object
ground.name = "Dark Ground"

ground_mat = bpy.data.materials.new("Dark Ground Material")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_links = ground_mat.node_tree.links
ground_nodes.clear()

ground_output = ground_nodes.new("ShaderNodeOutputMaterial")
ground_output.location = (300, 0)

ground_shader = ground_nodes.new("ShaderNodeBsdfPrincipled")
ground_shader.location = (0, 0)
ground_shader.inputs["Base Color"].default_value = (0.008, 0.012, 0.018, 1.0)
ground_shader.inputs["Roughness"].default_value = 0.82
ground_shader.inputs["Metallic"].default_value = 0.05

ground_links.new(ground_shader.outputs["BSDF"], ground_output.inputs["Surface"])
ground.data.materials.append(ground_mat)

# Cyan neon torus
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.14,
    major_segments=96,
    minor_segments=24,
    location=(0.0, 0.0, 0.45)
)
torus = bpy.context.object
torus.name = "Cyan Neon Ring"

for polygon in torus.data.polygons:
    polygon.use_smooth = True

neon_mat = bpy.data.materials.new("Cyan Neon Emission")
neon_mat.use_nodes = True
neon_nodes = neon_mat.node_tree.nodes
neon_links = neon_mat.node_tree.links
neon_nodes.clear()

neon_output = neon_nodes.new("ShaderNodeOutputMaterial")
neon_output.location = (320, 0)

emission = neon_nodes.new("ShaderNodeEmission")
emission.location = (0, 0)
emission.inputs["Color"].default_value = (0.0, 1.0, 1.0, 1.0)
emission.inputs["Strength"].default_value = 10.0

neon_links.new(emission.outputs["Emission"], neon_output.inputs["Surface"])
torus.data.materials.append(neon_mat)

# Set viewport display colors for clear material preview visibility
ground.color = (0.008, 0.012, 0.018, 1.0)
torus.color = (0.0, 1.0, 1.0, 1.0)

# Dark world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Dark World")
    bpy.context.scene.world = world

world.use_nodes = True
world_nodes = world.node_tree.nodes
world_background = world_nodes.get("Background")
if world_background:
    world_background.inputs["Color"].default_value = (0.001, 0.003, 0.006, 1.0)
    world_background.inputs["Strength"].default_value = 0.05
