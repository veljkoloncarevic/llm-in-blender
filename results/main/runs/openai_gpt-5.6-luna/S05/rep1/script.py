import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Dark ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0.0, 0.0, 0.0))
ground = bpy.context.object
ground.name = "Dark Ground"

ground_mat = bpy.data.materials.new("Dark Ground Material")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_links = ground_mat.node_tree.links

ground_nodes.clear()
ground_output = ground_nodes.new("ShaderNodeOutputMaterial")
ground_shader = ground_nodes.new("ShaderNodeBsdfPrincipled")
ground_shader.inputs["Base Color"].default_value = (0.008, 0.012, 0.018, 1.0)
ground_shader.inputs["Roughness"].default_value = 0.82
ground_shader.inputs["Metallic"].default_value = 0.05
ground_links.new(ground_shader.outputs["BSDF"], ground_output.inputs["Surface"])
ground.data.materials.append(ground_mat)

# Cyan neon torus
bpy.ops.mesh.primitive_torus_add(
    major_segments=96,
    minor_segments=24,
    location=(0.0, 0.0, 1.15),
    major_radius=2.0,
    minor_radius=0.14
)
ring = bpy.context.object
ring.name = "Cyan Neon Ring"

for polygon in ring.data.polygons:
    polygon.use_smooth = True

neon_mat = bpy.data.materials.new("Cyan Neon Emission")
neon_mat.use_nodes = True
neon_nodes = neon_mat.node_tree.nodes
neon_links = neon_mat.node_tree.links

neon_nodes.clear()
neon_output = neon_nodes.new("ShaderNodeOutputMaterial")
emission = neon_nodes.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (0.0, 1.0, 1.0, 1.0)
emission.inputs["Strength"].default_value = 10.0
neon_links.new(emission.outputs["Emission"], neon_output.inputs["Surface"])

ring.data.materials.append(neon_mat)

# Dark world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
world_nodes = world.node_tree.nodes
background = world_nodes.get("Background")
if background:
    background.inputs["Color"].default_value = (0.002, 0.004, 0.008, 1.0)
    background.inputs["Strength"].default_value = 0.02

# Optional compositor glow for supported render engines
scene = bpy.context.scene
scene.use_nodes = True
compositor_nodes = scene.node_tree.nodes
compositor_links = scene.node_tree.links
compositor_nodes.clear()

render_layers = compositor_nodes.new("CompositorNodeRLayers")
glare = compositor_nodes.new("CompositorNodeGlare")
glare.glare_type = "FOG_GLOW"
glare.quality = "HIGH"
glare.threshold = 0.5
glare.size = 7

composite = compositor_nodes.new("CompositorNodeComposite")
compositor_links.new(render_layers.outputs["Image"], glare.inputs["Image"])
compositor_links.new(glare.outputs["Image"], composite.inputs["Image"])
