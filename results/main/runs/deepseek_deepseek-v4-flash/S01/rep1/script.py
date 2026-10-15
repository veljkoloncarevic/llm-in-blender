import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create polished gold material
gold_mat = bpy.data.materials.new("Polished_Gold")
gold_mat.use_nodes = True
gold_bsdf = gold_mat.node_tree.nodes["Principled BSDF"]
gold_bsdf.inputs["Base Color"].default_value = (1.0, 0.766, 0.336, 1.0)
gold_bsdf.inputs["Metallic"].default_value = 1.0
gold_bsdf.inputs["Roughness"].default_value = 0.1

# Create neutral grey material for the ground
ground_mat = bpy.data.materials.new("Neutral_Grey")
ground_mat.use_nodes = True
ground_bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
ground_bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
ground_bsdf.inputs["Metallic"].default_value = 0.0
ground_bsdf.inputs["Roughness"].default_value = 0.8

# Create smooth UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)
sphere = bpy.context.object
sphere.name = "Sphere"
sphere.data.materials.append(gold_mat)
bpy.ops.object.shade_smooth()

# Create ground plane
bpy.ops.mesh.primitive_plane_add(
    size=10.0,
    location=(0.0, 0.0, 0.0)
)
plane = bpy.context.object
plane.name = "Ground"
plane.data.materials.append(ground_mat)
