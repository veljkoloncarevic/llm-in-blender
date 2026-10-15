import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
trunk_mat = bpy.data.materials.new("Trunk Brown")
trunk_mat.diffuse_color = (0.24, 0.09, 0.025, 1.0)

canopy_mat = bpy.data.materials.new("Canopy Green")
canopy_mat.diffuse_color = (0.08, 0. thirty, 0.06, 1.0)
