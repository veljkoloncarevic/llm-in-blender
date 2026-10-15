import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create smooth UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0.0, 0.0, 1.0))
sphere = bpy.context.active_object
bpy.ops.object.shade_smooth()

# Gold material
gold_mat = bpy.data.materials.new(name="Polished_Gold")
gold_mat.use_nodes = True
bsdf = gold_mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (1.0, 0.766, 0.336, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.1  # low roughness for polish

if sphere.data.materials:
    sphere.data.materials[0] = gold_mat
else:
    sphere.data.materials.append(gold_mat)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, 0.0))
plane = bpy.context.active_object

# Neutral grey ground material
ground_mat = bpy.data.materials.new(name="Neutral_Ground")
ground_mat.use_nodes = True
bsdf_ground = ground_mat.node_tree.nodes.get("Principled BSDF")
if bsdf_ground:
    bsdf_ground.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    bsdf_ground.inputs["Roughness"].default_value = 0.8

if plane.data.materials:
    plane.data.materials[0] = ground_mat
else:
    plane.data.materials.append(ground_mat)
