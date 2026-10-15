import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
plane = bpy.context.object
plane.name = "GroundPlane"

# Ground material (blue, slightly rough)
plane_mat = bpy.data.materials.new(name="GroundMaterial")
plane_mat.use_nodes = True
principled_plane = plane_mat.node_tree.nodes.get("Principled BSDF")
principled_plane.inputs["Base Color"].default_value = (0.0, 0.2, 1.0, 1.0)
principled_plane.inputs["Roughness"].default_value = 0.4
plane.data.materials.append(plane_mat)

# Create glass sphere (resting on ground plane: radius 1 ⇒ center z=1)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.object
sphere.name = "GlassSphere"

# Glass material (clear, transparent, IOR 1.45)
glass_mat = bpy.data.materials.new(name="GlassMaterial")
glass_mat.use_nodes = True
principled_glass = glass_mat.node_tree.nodes.get("Principled BSDF")
principled_glass.inputs["Transmission"].default_value = 1.0
principled_glass.inputs["Roughness"].default_value = 0.0
principled_glass.inputs["IOR"].default_value = 1.45
principled_glass.inputs["Alpha"].default_value = 1.0
sphere.data.materials.append(glass_mat)
