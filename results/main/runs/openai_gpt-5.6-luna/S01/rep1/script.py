import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove orphaned mesh and material data
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)
for material in list(bpy.data.materials):
    if material.users == 0:
        bpy.data.materials.remove(material)

# Create polished gold material
gold_material = bpy.data.materials.new(name="Polished Gold")
gold_material.use_nodes = True
gold_nodes = gold_material.node_tree.nodes
gold_principled = gold_nodes.get("Principled BSDF")

gold_principled.inputs["Base Color"].default_value = (0.83, 0.52, 0.12, 1.0)
gold_principled.inputs["Metallic"].default_value = 1.0
gold_principled.inputs["Roughness"].default_value = 0.12

# Create smooth UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=32,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)
sphere = bpy.context.object
sphere.name = "Polished Gold Sphere"

for polygon in sphere.data.polygons:
    polygon.use_smooth = True

sphere.data.materials.append(gold_material)

# Create neutral grey ground material
ground_material = bpy.data.materials.new(name="Neutral Grey Ground")
ground_material.use_nodes = True
ground_nodes = ground_material.node_tree.nodes
ground_principled = ground_nodes.get("Principled BSDF")

ground_principled.inputs["Base Color"].default_value = (0.35, 0.35, 0.35, 1.0)
ground_principled.inputs["Metallic"].default_value = 0.0
ground_principled.inputs["Roughness"].default_value = 0.5

# Create ground plane
bpy.ops.mesh.primitive_plane_add(
    size=20.0,
    location=(0.0, 0.0, 0.0)
)
ground = bpy.context.object
ground.name = "Neutral Grey Ground Plane"
ground.data.materials.append(ground_material)
