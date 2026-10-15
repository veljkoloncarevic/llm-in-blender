import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = "Sphere"
bpy.ops.object.shade_smooth()

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Ground"

# Gold material for the sphere
gold_mat = bpy.data.materials.new(name="Gold")
gold_mat.use_nodes = True
nodes = gold_mat.node_tree.nodes
links = gold_mat.node_tree.links
nodes.clear()

gold_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
gold_bsdf.inputs['Metallic'].default_value = 1.0
gold_bsdf.inputs['Roughness'].default_value = 0.1

out_node = nodes.new(type='ShaderNodeOutputMaterial')
links.new(gold_bsdf.outputs['BSDF'], out_node.inputs['Surface'])

# Neutral grey material for the ground
grey_mat = bpy.data.materials.new(name="Grey")
grey_mat.use_nodes = True
nodes = grey_mat.node_tree.nodes
links = grey_mat.node_tree.links
nodes.clear()

grey_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
grey_bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)
grey_bsdf.inputs['Metallic'].default_value = 0.0
grey_bsdf.inputs['Roughness'].default_value = 0.5

out_node = nodes.new(type='ShaderNodeOutputMaterial')
links.new(grey_bsdf.outputs['BSDF'], out_node.inputs['Surface'])

# Assign materials to objects
if not sphere.data.materials:
    sphere.data.materials.append(gold_mat)
else:
    sphere.data.materials[0] = gold_mat

if not plane.data.materials:
    plane.data.materials.append(grey_mat)
else:
    plane.data.materials[0] = grey_mat
