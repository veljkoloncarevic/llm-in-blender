import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create dark ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Create ground material
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
principled = ground_mat.node_tree.nodes.get("Principled BSDF")
principled.inputs["Base Color"].default_value = (0.01, 0.01, 0.01, 1)
principled.inputs["Roughness"].default_value = 0.8
ground.data.materials.append(ground_mat)

# Create glowing cyan neon ring (torus)
bpy.ops.mesh.primitive_torus_add(
    location=(0, 0, 0.5),
    major_radius=1.0,
    minor_radius=0.05,
    major_segments=128,
    minor_segments=32
)
torus = bpy.context.active_object
torus.name = "NeonRing"
bpy.ops.object.shade_smooth()

# Create neon material
neon_mat = bpy.data.materials.new(name="NeonMaterial")
neon_mat.use_nodes = True
principled = neon_mat.node_tree.nodes.get("Principled BSDF")
principled.inputs["Base Color"].default_value = (0, 0, 0, 1)
principled.inputs["Emission Color"].default_value = (0, 1, 1, 1)
principled.inputs["Emission Strength"].default_value = 10.0
torus.data.materials.append(neon_mat)
