import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
obj = bpy.context.active_object
obj.name = "CarPaintSphere"

# Create deep red car-paint material
mat = bpy.data.materials.new(name="DeepRedCarPaint")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf is None:
    bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")

# Configure the Principled BSDF
bsdf.inputs["Base Color"].default_value = (0.8, 0.02, 0.02, 1.0)  # Deep red
bsdf.inputs["Metallic"].default_value = 0.5
bsdf.inputs["Coat Weight"].default_value = 1.0  # Strong clear coat

# Assign material to sphere
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
