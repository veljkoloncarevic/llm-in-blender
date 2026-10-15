import bpy

# Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 1. Create a dark ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground_obj = bpy.active_object
ground_obj.name = "GroundPlane"

# Create dark material for the ground
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_nodes.clear()

# Add Principled BSDF for the ground
ground_bsdf = ground_nodes.new(type='ShaderNodeBsdfPrincipled')
ground_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
ground_bsdf.inputs['Roughness'].default_value = 0.4

ground_output = ground_nodes.new(type='ShaderNodeOutputMaterial')
ground_mat.node_tree.links.new(ground_bsdf.outputs['BSDF'], ground_output.inputs['Surface'])
ground_obj.data.materials.append(ground_mat)

# 2. Create the neon torus ring above the ground
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.2,
    major_segments=64,
    minor_segments=32,
    location=(0, 0, 2.0),
    rotation=(1.5708, 0, 0) # Rotate to stand vertically
)
torus_obj = bpy.active_object
torus_obj.name = "NeonRing"

# Apply smooth shading to the torus
for polygon in torus_obj.data.polygons:
    polygon.use_smooth = True

# Create glowing cyan emissive material
neon_mat = bpy.data.materials.new(name="NeonCyanMaterial")
neon_mat.use_nodes = True
neon_nodes = neon_mat.node_tree.nodes
neon_nodes.clear()

# Add Emission shader
emission_node = neon_nodes.new(type='ShaderNodeEmission')
# Cyan color
emission_node.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0)
# High emission strength (at least 5 as requested)
emission_node.inputs['Strength'].default_value = 15.0

neon_output = neon_nodes.new(type='ShaderNodeOutputMaterial')
neon_mat.node_tree.links.new(emission_node.outputs['Emission'], neon_output.inputs['Surface'])
torus_obj.data.materials.append(neon_mat)
