import bpy
import bmesh

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere mesh (5 subdivisions => 20,480 faces, within 2,000–60,000)
mesh = bpy.data.meshes.new("RockMesh")
bm = bmesh.new()
bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
bm.to_mesh(mesh)
bm.free()

# Create and link the object
obj = bpy.data.objects.new("Rock", mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Irregular non-uniform scale for a natural rock silhouette
obj.scale = (0.8, 1.2, 0.7)

# Add Displace modifier driven by a 3D noise texture
mod = obj.modifiers.new(name="DisplaceRock", type='DISPLACE')
tex = bpy.data.textures.new("RockNoise", type='NOISE')
tex.noise_type = 'RIDGED_MULTIFRACTAL'
tex.noise_scale = 0.8
mod.texture = tex
mod.texture_coords = 'LOCAL'
mod.strength = 0.35
mod.mid_level = 0.5
