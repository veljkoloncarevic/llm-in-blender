import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.scale = (10, 10, 1)

# Create glass sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = "GlassSphere"

# Smooth shading for sphere
mesh = sphere.data
for poly in mesh.polygons:
    poly.use_smooth = True

# Create glass material
glass_mat = bpy.data.materials.new(name="GlassMaterial")
glass_mat.use_nodes = True
nodes = glass_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled is not None:
    principled.inputs["Transmission"].default_value = 1.0
    principled.inputs["Roughness"].default_value = 0.01
    principled.inputs["IOR"].default_value = 1.45

# Assign glass material to sphere
if sphere.data.materials:
    sphere.data.materials[0] = glass_mat
else:
    sphere.data.materials.append(glass_mat)

# Create blue ground material
ground_mat = bpy.data.materials.new(name="BlueGround")
ground_mat.use_nodes = True
nodes = ground_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled is not None:
    principled.inputs["Base Color"].default_value = (0.0, 0.1, 0.8, 1.0)
    principled.inputs["Roughness"].default_value = 0.5

# Assign ground material to plane
if ground.data.materials:
    ground.data.materials[0] = ground_mat
else:
    ground.data.materials.append(ground_mat)
