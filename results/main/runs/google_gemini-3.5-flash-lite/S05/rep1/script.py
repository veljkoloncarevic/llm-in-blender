import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground_plane = bpy.object.active if hasattr(bpy, 'object') else bpy.context.active_object
ground_plane.name = "GroundPlane"

# Create dark material for ground plane
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_nodes.clear()

# Setup Principled BSDF for dark, slightly reflective ground
ground_principled = ground_nodes.new(type='ShaderNodeBsdfPrincipled')
ground_principled.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
ground_principled.inputs['Roughness'].default_value = 0.2

ground_output = ground_nodes.new(type='ShaderNodeOutputMaterial')
ground_mat.node_tree.links.new(ground_principled.outputs['BSDF'], ground_output.inputs['Surface'])
ground_plane.data.materials.append(ground_mat)

# Create torus (neon ring)
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.15,
    major_segments=64,
    minor_segments=32,
    location=(0, 0, 1.5),
    rotation=(1.5708, 0, 0) # Rotate to stand upright facing forward/up
)
neon_ring = bpy.context.active_object
neon_ring.name = "NeonRing"

# Create glowing cyan emission material
neon_mat = bpy.data.materials.new(name="CyanNeonMaterial")
neon_mat.use_nodes = True
neon_nodes = neon_mat.node_tree.nodes
neon_nodes.clear()

# Emission Node
emission_node = neon_nodes.new(type='ShaderNodeEmission')
# Cyan color with high intensity
emission_node.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0)
emission_node.inputs['Strength'].default_value = 25.0

# Material Output Node
neon_output = neon_nodes.new(type='ShaderNodeOutputMaterial')

# Link Emission to Output
neon_mat.node_tree.links.new(emission_node.outputs['Emission'], neon_output.inputs['Surface'])

# Assign material to torus
neon_ring.data.materials.append(neon_mat)

# Set world background to dark to let the neon glow pop
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
world_nodes = world.node_tree.nodes
world_nodes.clear()
bg_node = world_nodes.new(type='ShaderNodeBackground')
bg_node.inputs['Color'].default_value = (0.01, 0.01, 0.01, 1.0)
bg_node.inputs['Strength'].default_value = 1.0
world_output = world_nodes.new(type='ShaderNodeOutputWorld')
world.node_tree.links.new(bg_node.outputs['Background'], world_output.inputs['Surface'])
