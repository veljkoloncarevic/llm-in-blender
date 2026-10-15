import bpy

# Clear existing objects in the scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Create a smooth UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32, location=(0, 0, 1.0))
sphere = bpy.active_object
sphere.name = "GoldSphere"

# Apply smooth shading to the sphere
for face in sphere.data.polygons:
    face.use_smooth = True

# 2. Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
ground = bpy.active_object
ground.name = "GroundPlane"

# 3. Create and assign the Polished Gold material for the sphere
gold_mat = bpy.data.materials.new(name="PolishedGold")
gold_mat.use_nodes = True
gold_nodes = gold_mat.node_tree.nodes
gold_links = gold_mat.node_tree.links

# Clear default nodes
gold_nodes.clear()

# Add Material Output and Principled BSDF
gold_output = gold_nodes.new(type='ShaderNodeOutputMaterial')
gold_output.location = (300, 0)

gold_principled = gold_nodes.new(type='ShaderNodeBsdfPrincipled')
gold_principled.location = (0, 0)
# Set gold properties: Metallic 1.0, warm gold base color, low roughness
gold_principled.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
gold_principled.inputs['Metallic'].default_value = 1.0
gold_principled.inputs['Roughness'].default_value = 0.1

gold_links.new(gold_principled.outputs['BSDF'], gold_output.inputs['Surface'])
sphere.data.materials.append(gold_mat)

# 4. Create and assign the Neutral Grey material for the ground plane
grey_mat = bpy.data.materials.new(name="NeutralGrey")
grey_mat.use_nodes = True
grey_nodes = grey_mat.node_tree.nodes
grey_links = grey_mat.node_tree.links

# Clear default nodes
grey_nodes.clear()

# Add Material Output and Principled BSDF
grey_output = grey_nodes.new(type='ShaderNodeOutputMaterial')
grey_output.location = (300, 0)

grey_principled = grey_nodes.new(type='ShaderNodeBsdfPrincipled')
grey_principled.location = (0, 0)
# Set neutral grey properties: mid-grey base color, matte roughness
grey_principled.inputs['Base Color'].default_value = (0.2, 0.2, 0.2, 1.0)
grey_principled.inputs['Roughness'].default_value = 0.7

grey_links.new(grey_principled.outputs['BSDF'], grey_output.inputs['Surface'])
ground.data.materials.append(grey_mat)
