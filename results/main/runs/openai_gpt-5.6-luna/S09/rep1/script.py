import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=128,
    ring_count=64,
    radius=1.0,
    location=(0.0, 0.0, 0.0)
)
sphere = bpy.context.object
sphere.name = "Deep Red Car Paint Sphere"

# Smooth shading
for polygon in sphere.data.polygons:
    polygon.use_smooth = True

# Create the deep red car-paint material
material = bpy.data.materials.new(name="Deep Red Car Paint")
material.use_nodes = True

nodes = material.node_tree.nodes
principled = nodes.get("Principled BSDF")

principled.inputs["Base Color"].default_value = (0.32, 0.008, 0.012, 1.0)
principled.inputs["Metallic"].default_value = 0.5
principled.inputs["Roughness"].default_value = 0.2
principled.inputs["Coat Weight"].default_value = 0.95
principled.inputs["Coat Roughness"].default_value = 0.08

sphere.data.materials.append(material)
