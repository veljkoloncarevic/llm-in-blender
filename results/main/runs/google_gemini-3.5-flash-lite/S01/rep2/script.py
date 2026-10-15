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

# 3. Create and assign Polished Gold Material to the Sphere
gold_mat = bpy.data.materials.new(name="PolishedGold")
gold_mat.use_nodes = True
gold_nodes = gold_mat.node_tree.nodes
gold_links = gold_mat.node_tree.links

# Clear default nodes
gold_nodes.clear()

# Add Principled BSDF and Material Output
gold_output = gold_nodes.new(type='ShaderNodeOutputMaterial')
gold_output.location = (300, 0)

gold_bsdf = gold_nodes.new(type='ShaderNodeBsdfPrincipled')
gold_bsdf.location = (0, 0)

# Set gold properties (Metallic 1.0, Warm Gold Base Color, Low Roughness)
gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
gold_bsdf.inputs['Metallic'].default_value = 1.0
gold_bsdf.inputs['Roughness'].default_value = 0.1

# Link Principled BSDF to Material Output
gold_links.new(gold_bsdf.outputs['BSDF'], gold_output.inputs['Surface'])

# Assign gold material to sphere
sphere.data.materials.append(gold_mat)

# 4. Create and assign Neutral Grey Material to the Ground Plane
grey_mat = bpy.data.materials.new(name="NeutralGreyGround")
grey_mat.use_nodes = True
grey_nodes = grey_mat.node_tree.nodes
grey_links = grey_mat.node_tree.links

# Clear default nodes
grey_nodes.clear()

# Add Principled BSDF and Material Output
grey_output = grey_nodes.new(type='ShaderNodeOutputMaterial')
grey_output.location = (300, 0)

grey_bsdf = grey_nodes.new(type='ShaderNodeBsdfPrincipled')
grey_bsdf.location = (0, 0)

# Set neutral grey properties
grey_bsdf.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)
grey_bsdf.inputs['Roughness'].default_value = 0.4

# Link Principled BSDF to Material Output
grey_links.new(grey_bsdf.outputs['BSDF'], grey_output.inputs['Surface'])

# Assign grey material to ground plane
ground.data.materials.append(grey_mat)
