import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object

# Create gold material for sphere
gold_material = bpy.data.materials.new(name="Gold")
gold_material.use_nodes = True
bsdf = gold_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.843, 0.0, 1.0)  # Gold color
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.2

# Assign gold material to sphere
sphere.data.materials.append(gold_material)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.active_object

# Create grey material for plane
grey_material = bpy.data.materials.new(name="Grey")
grey_material.use_nodes = True
bsdf_grey = grey_material.node_tree.nodes["Principled BSDF"]
bsdf_grey.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)  # Neutral grey
bsdf_grey.inputs["Metallic"].default_value = 0.0
bsdf_grey.inputs["Roughness"].default_value = 0.5

# Assign grey material to plane
plane.data.materials.append(grey_material)
