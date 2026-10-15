import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove orphaned mesh and material data where possible
for datablocks in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)

# Create blue ground material
ground_material = bpy.data.materials.new("Blue Ground Material")
ground_material.use_nodes = True

ground_bsdf = ground_material.node_tree.nodes.get("Principled BSDF")
ground_bsdf.inputs["Base Color"].default_value = (0.015, 0.08, 0.35, 1.0)
ground_bsdf.inputs["Roughness"].default_value = 0.42
ground_bsdf.inputs["Metallic"].default_value = 0.0

# Create ground plane
bpy.ops.mesh.primitive_plane_add(
    size=12.0,
    location=(0.0, 0.0, 0.0)
)
ground = bpy.context.active_object
ground.name = "Blue Ground Plane"
ground.data.name = "Blue Ground Plane Mesh"
ground.data.materials.append(ground_material)

# Create clear glass material
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

# Create glass sphere, tangent to the ground plane
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=32,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)
sphere = bpy.context.active_object
sphere.name = "Clear Glass Sphere"
sphere.data.name = "Clear Glass Sphere Mesh"
sphere.data.materials.append(glass_material)

# Smooth shading
for polygon in sphere.data.polygons:
    polygon.use_smooth = True

# Ensure the sphere is centered precisely above the plane
sphere.location.z = 1.0
