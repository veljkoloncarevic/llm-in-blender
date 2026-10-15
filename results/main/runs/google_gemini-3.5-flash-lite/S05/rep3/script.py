import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create a dark ground plane
bpy.ops.mesh.primitive_plane_size = 10.0
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground_obj = bpy.context.active_object
ground_obj.name = "GroundPlane"

# Create dark matte material for the ground
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_nodes.clear()

# Add Principled BSDF and Material Output
ground_bsdf = ground_nodes.ShaderNodeBsdfPrincipled(name="Principled BSDF")
ground_bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
ground_bsdf.inputs['Roughness'].default_value = 0.4

ground_out = ground_nodes.ShaderNodeOutputMaterial(name="Material Output")
ground_mat.node_tree.links.new(ground_bsdf.outputs['BSDF'], ground_out.inputs['Surface'])
ground_obj.data.materials.append(ground_mat)


# 2. Create the neon torus ring
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.15,
    major_segments=64,
    minor_segments=32,
    location=(0, 0, 1.5),
    rotation=(1.5708, 0, 0) # Rotate to stand vertically
)
ring_obj = bpy.context.active_object
ring_obj.name = "NeonRing"

# Apply smooth shading to torus
for face in ring_obj.data.polygons:
    face.use_smooth = True

# Create glowing cyan emission material
ring_mat = bpy.data.materials.new(name="NeonCyanMaterial")
ring_mat.use_nodes = True
ring_nodes = ring_mat.node_tree.nodes
ring_nodes.clear()

# Add Emission shader
emission_node = ring_nodes.ShaderNodeEmission(name="Emission")
emission_node.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0) # Cyan
emission_node.inputs['Strength'].default_value = 15.0 # Greater than 5

ring_out = ring_nodes.ShaderNodeOutputMaterial(name="Material Output")
ring_mat.node_tree.links.new(emission_node.outputs['Emission'], ring_out.inputs['Surface'])
ring_obj.data.materials.append(ring_mat)
