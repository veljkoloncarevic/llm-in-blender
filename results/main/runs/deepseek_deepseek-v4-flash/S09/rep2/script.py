import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object

# Create a deep red car-paint material
mat = bpy.data.materials.new(name="DeepRedCarPaint")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Get the Principled BSDF node
principled = nodes.get("Principled BSDF")
if principled is None:
    # Fallback if not found
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")

# Set base color (deep red)
principled.inputs["Base Color"].default_value = (0.55, 0.0, 0.0, 1.0)

# Metallic around 0.5
principled.inputs["Metallic"].default_value = 0.5

# Low roughness for a polished base coat
principled.inputs["Roughness"].default_value = 0.3

# Strong clear coat
principled.inputs["Coat Weight"].default_value = 0.9
principled.inputs["Coat Roughness"].default_value = 0.1
principled.inputs["Coat IOR"].default_value = 1.5

# Ensure Principled BSDF is connected to the Material Output
material_output = nodes.get("Material Output")
if material_output is None:
    material_output = nodes.new(type="ShaderNodeOutputMaterial")

if not principled.outputs["BSDF"].links:
    links.new(principled.outputs["BSDF"], material_output.inputs["Surface"])

# Assign material to the sphere
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
