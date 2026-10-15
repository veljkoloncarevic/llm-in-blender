import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a UV Sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0, 
    segments=64, 
    ring_count=32, 
    location=(0, 0, 0)
)
sphere = bpy.active_object
sphere.name = "CarPaintSphere"

# Apply smooth shading to the sphere
for face in sphere.data.polygons:
    face.use_smooth = True

# Create a new material for the deep red car paint
car_paint_mat = bpy.data.materials.new(name="DeepRedCarPaint")
car_paint_mat.use_nodes = True
nodes = car_paint_mat.node_tree.nodes
links = car_paint_mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add Principled BSDF node
principled_node = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_node.location = (0, 0)

# Configure Car Paint properties
# Deep Red Base Color
principled_node.inputs['Base Color'].default_value = (0.18, 0.005, 0.008, 1.0)

# Metallic (around 0.5)
principled_node.inputs['Metallic'].default_value = 0.5

# Roughness (low roughness for a shiny, polished car paint look)
principled_node.inputs['Roughness'].default_value = 0.15

# Strong Clear Coat (at least 0.8)
principled_node.inputs['Coat Weight'].default_value = 1.0
principled_node.inputs['Coat Roughness'].default_value = 0.03
principled_node.inputs['Coat IOR'].default_value = 1.5

# Add Material Output node
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (300, 0)

# Link Principled BSDF to Material Output
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to the sphere
if sphere.data.materials:
    sphere.data.materials[0] = car_paint_mat
else:
    sphere.data.materials.append(car_paint_mat)
