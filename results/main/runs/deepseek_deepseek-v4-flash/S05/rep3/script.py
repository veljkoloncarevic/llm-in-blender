import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the glowing neon ring (torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0,
    minor_radius=0.1,
    location=(0.0, 0.0, 1.0)
)
torus = bpy.context.object
torus.name = "NeonRing"

# Create emissive cyan material for the ring
mat = bpy.data.materials.new(name="NeonCyanMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Emission node with cyan color and high strength
emission = nodes.new(type='ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0)
emission.inputs['Strength'].default_value = 10.0

# Output node and link
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Assign material to torus
if torus.data.materials:
    torus.data.materials[0] = mat
else:
    torus.data.materials.append(mat)

# Create dark ground plane
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.object
ground.name = "DarkGroundPlane"

# Dark, rough material for the ground
ground_mat = bpy.data.materials.new(name="DarkGroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_nodes.clear()

bsdf = ground_nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs['Roughness'].default_value = 1.0

ground_output = ground_nodes.new(type='ShaderNodeOutputMaterial')
ground_links = ground_mat.node_tree.links
ground_links.new(bsdf.outputs['BSDF'], ground_output.inputs['Surface'])

if ground.data.materials:
    ground.data.materials[0] = ground_mat
else:
    ground.data.materials.append(ground_mat)

# Smooth shading for the ring
bpy.ops.object.select_all(action='DESELECT')
torus.select_set(True)
bpy.context.view_layer.objects.active = torus
bpy.ops.object.shade_smooth()
