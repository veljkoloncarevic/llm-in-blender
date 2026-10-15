import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    if datablocks != bpy.data.materials:
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)

# Create blue ground plane
ground_mesh = bpy.data.meshes.new("GroundPlaneMesh")
ground_mesh.from_pydata(
    [(-10, -10, 0), (10, -10, 0), (10, 10, 0), (-10, 10, 0)],
    [],
    [(0, 1, 2, 3)]
)
ground_mesh.update()

ground = bpy.data.objects.new("Blue Ground Plane", ground_mesh)
bpy.context.collection.objects.link(ground)

ground_material = bpy.data.materials.new("Blue Ground Material")
ground_material.use_nodes = True
ground_bsdf = ground_material.node_tree.nodes.get("Principled BSDF")
ground_bsdf.inputs["Base Color"].default_value = (0.015, 0.12, 0.8, 1.0)
ground_bsdf.inputs["Roughness"].default_value = 0.32
ground_bsdf.inputs["Metallic"].default_value = 0.0
ground.data.materials.append(ground_material)

# Create glass sphere resting on the plane
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=32,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)
sphere = bpy.context.object
sphere.name = "Clear Glass Sphere"

bpy.ops.object.shade_smooth()

glass_material = bpy.data.materials.new("Clear Glass Material")
glass_material.use_nodes = True
glass_bsdf = glass_material.node_tree.nodes.get("Principled BSDF")
glass_bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
glass_bsdf.inputs["Metallic"].default_value = 0.0
glass_bsdf.inputs["Roughness"].default_value = 0.01
glass_bsdf.inputs["IOR"].default_value = 1.45

if "Transmission Weight" in glass_bsdf.inputs:
    glass_bsdf.inputs["Transmission Weight"].default_value = 1.0
elif "Transmission" in glass_bsdf.inputs:
    glass_bsdf.inputs["Transmission"].default_value = 1.0

sphere.data.materials.append(glass_material)
