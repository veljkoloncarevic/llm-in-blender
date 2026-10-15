import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground_plane = bpy.context.active_object
ground_plane.name = "GroundPlane"

# Create blue material for ground plane
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.3, 0.8, 1.0)
ground_plane.data.materials.append(ground_mat)

# Create a glass sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
sphere = bpy.context.active_object
sphere.name = "GlassSphere"

# Create glass material with Principled BSDF
glass_mat = bpy.data.materials.new(name="GlassMaterial")
glass_mat.use_nodes = True
principled = glass_mat.node_tree.nodes["Principled BSDF"]

# Set glass material properties
principled.inputs["Transmission"].default_value = 1.0  # Full transmission
principled.inputs["Roughness"].default_value = 0.01  # Near 0 roughness
principled.inputs["IOR"].default_value = 1.45  # Glass IOR
principled.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)  # White base color

sphere.data.materials.append(glass_mat)

# Ensure the viewport shading shows materials correctly
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
