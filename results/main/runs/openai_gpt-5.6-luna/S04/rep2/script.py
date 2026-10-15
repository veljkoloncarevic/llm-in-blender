import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create blue ground plane
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0.0, 0.0, 0.0))
ground = bpy.context.object
ground.name = "Blue Ground Plane"

ground_material = bpy.data.materials.new("Blue Ground Material")
ground_material.use_nodes = True
ground_bsdf = ground_material.node_tree.nodes.get("Principled BSDF")
ground_bsdf.inputs["Base Color"].default_value = (0.015, 0.12, 0.8, 1.0)
ground_bsdf.inputs["Roughness"].default_value = 0.4
ground_bsdf.inputs["Metallic"].default_value = 0.0
ground.data.materials.append(ground_material)

# Create clear glass sphere resting on the plane
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=96,
    ring_count=64,
    radius=1.0,
    location=(0.0, 0.0, 1.0)
)
sphere = bpy.context.object
sphere.name = "Clear Glass Sphere"

for polygon in sphere.data.polygons:
    polygon.use_smooth = True

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

glass_bsdf.inputs["Alpha"].default_value = 1.0
sphere.data.materials.append(glass_material)

# Neutral world background for visibility
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world

world.use_nodes = True
world_background = world.node_tree.nodes.get("Background")
world_background.inputs["Color"].default_value = (0.035, 0.035, 0.035, 1.0)
world_background.inputs["Strength"].default_value = 0.3
