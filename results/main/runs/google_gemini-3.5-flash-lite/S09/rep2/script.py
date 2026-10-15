import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a UV Sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0, 
    segments=64, 
    ring_count=32, 
    location=(0, 0, 0)
)
sphere_obj = bpy.active_object
sphere_obj.name = "CarPaintSphere"

# Smooth shading for the sphere
for polygon in sphere_obj.data.polygons:
    polygon.use_smooth = True

# 3. Create Deep Red Car-Paint Material
material = bpy.data.materials.new(name="DeepRedCarPaint")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes to build cleanly
nodes.clear()

# Create Principled BSDF node
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (0, 0)

# Configure Car-Paint properties
# Deep red base color
principled_node.inputs['Base Color'].default_value = (0.15, 0.01, 0.01, 1.0)
# Metallic finish
principled_node.inputs['Metallic'].default_value = 0.5
# Slight roughness for the metallic flake appearance beneath
principled_node.inputs['Roughness'].default_value = 0.25
# Strong clear coat layer
principled_node.inputs['Coat Weight'].default_value = 1.0
principled_node.inputs['Coat Roughness'].default_value = 0.03
principled_node.inputs['Coat IOR'].default_value = 1.5

# Create Material Output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (300, 0)

# Link Principled BSDF to Material Output
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to the sphere
if sphere_obj.data.materials:
    sphere_obj.data.materials[0] = material
else:
    sphere_obj.data.materials.append(material)
