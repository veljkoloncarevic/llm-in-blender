import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=32,
    radius=1.0,
    location=(0.0, 0.0, 0.0)
)
sphere = bpy.context.active_object
sphere.name = "Deep Red Car Paint Sphere"

# Smooth shading
for polygon in sphere.data.polygons:
    polygon.use_smooth = True

# Create deep red metallic car-paint material
material = bpy.data.materials.new(name="Deep Red Car Paint")
material.use_nodes = True

nodes = material.node_tree.nodes
principled = nodes.get("Principled BSDF")

principled.inputs["Base Color"].default_value = (0.20, 0.006, 0.008, 1.0)
principled.inputs["Metallic"].default_value = 0.5
principled.inputs["Roughness"].default_value = 0.22
principled.inputs["Coat Weight"].default_value = 0.9
principled.inputs["Coat Roughness"].default_value = 0.08

# Assign material
sphere.data.materials.append(material)
