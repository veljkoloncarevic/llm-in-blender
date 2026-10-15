import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create clear glass sphere resting on the ground plane
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.object
sphere.name = "GlassSphere"
bpy.ops.object.shade_smooth()

glass_mat = bpy.data.materials.new("GlassMaterial")
glass_mat.use_nodes = True
bsdf = glass_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Transmission"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.02
bsdf.inputs["IOR"].default_value = 1.45

if sphere.data.materials:
    sphere.data.materials[0] = glass_mat
else:
    sphere.data.materials.append(glass_mat)

# Create blue ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.object
plane.name = "GroundPlane"

ground_mat = bpy.data.materials.new("BlueGround")
ground_mat.use_nodes = True
ground_bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
ground_bsdf.inputs["Base Color"].default_value = (0.1, 0.2, 0.8, 1.0)
ground_bsdf.inputs["Roughness"].default_value = 0.4

if plane.data.materials:
    plane.data.materials[0] = ground_mat
else:
    plane.data.materials.append(ground_mat)
