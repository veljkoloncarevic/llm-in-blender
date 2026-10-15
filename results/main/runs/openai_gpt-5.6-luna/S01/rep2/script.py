import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create polished gold material
gold_material = bpy.data.materials.new(name="Polished Gold")
gold_material.use_nodes = True

gold_bsdf = gold_material.node_tree.nodes.get("Principled BSDF")
gold_bsdf.inputs["Base Color"].default_value = (1.0, 0.55, 0.08, 1.0)
gold_bsdf.inputs["Metallic"].default_value = 1.0
gold_bsdf.inputs["Roughness"].default_value = 0.12

gold_material.diffuse_color = (1.0, 0.55, 0.08, 1.0)

# Create smooth UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=32,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)
sphere = bpy.context.object
sphere.name = "Polished Gold Sphere"
sphere.data.materials.append(gold_material)

for polygon in sphere.data.polygons:
    polygon.use_smooth = True

# Create neutral grey ground material
ground_material = bpy.data.materials.new(name="Neutral Grey Ground")
ground_material.use_nodes = True

ground_bsdf = ground_material.node_tree.nodes.get("Principled BSDF")
ground_bsdf.inputs["Base Color"].default_value = (0.18, 0.18, 0.18, 1.0)
ground_bsdf.inputs["Metallic"].default_value = 0.0
ground_bsdf.inputs["Roughness"].default_value = 0.65

ground_material.diffuse_color = (0.18, 0.18, 0.18, 1.0)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(
    size=20.0,
    location=(0.0, 0.0, 0.0)
)
ground = bpy.context.object
ground.name = "Neutral Grey Ground Plane"
ground.data.materials.append(ground_material)
