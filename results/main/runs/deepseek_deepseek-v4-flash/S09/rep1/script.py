import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
obj = bpy.context.active_object
obj.name = "CarPaintSphere"

# Create deep red car-paint material
mat = bpy.data.materials.new(name="DeepRedCarPaint")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Principled BSDF node
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.inputs['Base Color'].default_value = (0.8, 0.0, 0.0, 1.0)  # deep red
principled.inputs['Metallic'].default_value = 0.5
principled.inputs['Coat Weight'].default_value = 1.0

# Output node
output = nodes.new(type='ShaderNodeOutputMaterial')
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Assign material to sphere
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
