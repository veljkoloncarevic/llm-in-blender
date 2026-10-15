import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a smooth UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32, location=(0, 0, 1.0))
sphere = bpy.active_object
sphere.name = "GoldSphere"

# Apply smooth shading to the sphere
for polygon in sphere.data.polygons:
    polygon.use_smooth = True

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0, 0, 0))
ground = bpy.active_object
ground.name = "GroundPlane"

# --- Material 1: Polished Gold ---
gold_mat = bpy.data.materials.new(name="PolishedGold")
gold_mat.use_nodes = True
nodes_gold = gold_mat.node_tree.nodes
links_gold = gold_mat.node_tree.links

# Clear default nodes just in case
nodes_gold.clear()

# Add Principled BSDF and Material Output
node_principled_gold = nodes_gold.new(type='ShaderNodeBsdfPrincipled')
node_principled_gold.location = (0, 0)

node_output_gold = nodes_gold.new(type='ShaderNodeOutputMaterial')
node_output_gold.location = (300, 0)

# Configure Gold properties
# Base Color: Rich metallic gold (RGB ~ 1.0, 0.766, 0.336)
node_principled_gold.inputs['Base Color'].default_value = (1.0, 0.766, 0.336, 1.0)
node_principled_gold.inputs['Metallic'].default_value = 1.0
node_principled_gold.inputs['Roughness'].default_value = 0.1

# Link Principled to Output
links_gold.new(node_principled_gold.outputs['BSDF'], node_output_gold.inputs['Surface'])

# Assign gold material to the sphere
if sphere.data.materials:
    sphere.data.materials[0] = gold_mat
else:
    sphere.data.materials.append(gold_mat)


# --- Material 2: Neutral Grey Ground ---
grey_mat = bpy.data.materials.new(name="NeutralGrey")
grey_mat.use_nodes = True
nodes_grey = grey_mat.node_tree.nodes
links_grey = grey_mat.node_tree.links

nodes_grey.clear()

node_principled_grey = nodes_grey.new(type='ShaderNodeBsdfPrincipled')
node_principled_grey.location = (0, 0)

node_output_grey = nodes_grey.new(type='ShaderNodeOutputMaterial')
node_output_grey.location = (300, 0)

# Configure Grey properties
node_principled_grey.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)
node_principled_grey.inputs['Roughness'].default_value = 0.6

# Link Principled to Output
links_grey.new(node_principled_grey.outputs['BSDF'], node_output_grey.inputs['Surface'])

# Assign grey material to the ground plane
if ground.data.materials:
    ground.data.materials[0] = grey_mat
else:
    ground.data.materials.append(grey_mat)
