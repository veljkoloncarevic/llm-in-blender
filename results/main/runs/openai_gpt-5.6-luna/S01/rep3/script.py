import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused mesh and material data
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)

# Create polished gold material
gold_material = bpy.data.materials.new(name="Polished Gold")
gold_material.use_nodes = True

gold_bsdf = gold_material.node_tree.nodes.get("Principled BSDF")
gold_bsdf.inputs["Base Color"].default_value = (1.0, 0.766, 0.336, 1.0)
gold_bsdf.inputs["Metallic"].default_value = 1.0
gold_bsdf.inputs["Roughness"].default_value = 0.12

# Create smooth UV sphere resting on the ground plane
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
ground_bsdf.inputs["Roughness"].default_value = 0.45

# Create ground plane
bpy.ops.mesh.primitive_plane_add(
    size=20.0,
    location=(0.0, 0.0, 0.0)
)
ground = bpy.context.object
ground.name = "Neutral Grey Ground Plane"
ground.data.materials.append(ground_material)
