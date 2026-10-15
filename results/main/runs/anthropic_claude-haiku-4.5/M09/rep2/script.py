import bpy
import bmesh
from mathutils import Vector
import random

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create icosphere with 4 subdivisions
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1,
    location=(0, 0, 0)
)
sphere = bpy.context.active_object
sphere.name = "Rock"

# Apply non-uniform scale for irregular shape
sphere.scale = (
    random.uniform(0.8, 1.3),
    random.uniform(0.7, 1.2),
    random.uniform(0.9, 1.4)
)
bpy.context.view_layer.objects.active = sphere
bpy.ops.object.transform_apply(scale=True)

# Subdivide the mesh to get more geometry (4+ subdivisions)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
for _ in range(4):
    bpy.ops.mesh.subdivide()
bpy.ops.object.mode_set(mode='OBJECT')

# Create a noise texture for displacement
noise_texture = bpy.data.textures.new("RockNoise", type='CLOUDS')
noise_texture.cloud_type = 'COLOR'
noise_texture.noise_scale = 2.5
noise_texture.noise_basis = 'PERLIN'

# Create material and add texture
material = bpy.data.materials.new("RockMaterial")
material.use_nodes = True
bsdf = material.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.4, 0.35, 0.3, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8

sphere.data.materials.append(material)

# Add Displace modifier with noise texture
displace_mod = sphere.modifiers.new(name="DisplaceRock", type='DISPLACE')
displace_mod.texture = noise_texture
displace_mod.strength = 0.15
displace_mod.mid_level = 0.5

# Add some additional deformation with a second displacement
noise_texture2 = bpy.data.textures.new("RockNoise2", type='CLOUDS')
noise_texture2.cloud_type = 'COLOR'
noise_texture2.noise_scale = 5.0
noise_texture2.noise_basis = 'PERLIN'

displace_mod2 = sphere.modifiers.new(name="DisplaceRock2", type='DISPLACE')
displace_mod2.texture = noise_texture2
displace_mod2.strength = 0.08
displace_mod2.mid_level = 0.5

# Apply a smooth modifier for more natural look
smooth_mod = sphere.modifiers.new(name="Smooth", type='SMOOTH')
smooth_mod.factor = 0.3
smooth_mod.iterations = 2

# Check face count
bpy.ops.object.shade_smooth()
sphere.select_set(True)
bpy.context.view_layer.objects.active = sphere

# Get face count after all modifiers
bpy.ops.object.mode_set(mode='OBJECT')
face_count = len(sphere.data.polygons)

print(f"Rock created with {face_count} faces")
