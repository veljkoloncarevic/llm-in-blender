import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, segments=64, ring_count=32)
sphere = bpy.active_object
sphere.name = "CarPaintSphere"

# Apply smooth shading to the sphere
for face in sphere.data.polygons:
    face.use_smooth = True

# Create a new material for the car paint effect
material = bpy.data.materials.new(name="DeepRedCarPaint")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes to start fresh
nodes.clear()

# Create Output Node
node_output = nodes.new(type='ShaderNodeOutputMaterial')
node_output.location = (400, 0)

# Create Principled BSDF Node
node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
node_principled.location = (0, 0)

# Configure Principled BSDF parameters for deep red car paint
# Deep red base color
node_principled.inputs['Base Color'].default_value = (0.05, 0.0, 0.0, 1.0)
# Metallic factor around 0.5
node_principled.inputs['Metallic'].default_value = 0.5
# Slight roughness for the base coat metallic flakes look
node_principled.inputs['Roughness'].default_value = 0.2
# Strong clear coat (at least 0.8)
node_principled.inputs['Coat Weight'].default_value = 1.0
# Clear coat roughness for a glossy, wet finish
node_principled.inputs['Coat Roughness'].default_value = 0.03
# Index of refraction for the clear coat layer
node_principled.inputs['Coat IOR'].default_value = 1.5

# Link Principled BSDF to Material Output
links.new(node_principled.outputs['BSDF'], node_output.inputs['Surface'])

# Assign the material to the sphere
if sphere.data.materials:
    sphere.data.materials[0] = material
else:
    sphere.data.materials.append(material)
