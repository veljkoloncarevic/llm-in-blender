import bpy
import bmesh
from mathutils import Vector
import random

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Create icosphere with 4 subdivisions
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1,
    location=(0, 0, 0)
)
obj = bpy.context.active_object
mesh = obj.data

# Convert to icosphere by using bmesh subdivision
bm = bmesh.new()
bm.from_mesh(mesh)

# Apply catmull-clark subdivision 4 times to get enough geometry
for _ in range(4):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0.0)
    bpy.ops.object.mode_set(mode='OBJECT')

# Get face count
mesh = obj.data
face_count = len(mesh.polygons)
print(f"Initial face count: {face_count}")

# Apply non-uniform scaling to the base geometry
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(
    random.uniform(0.8, 1.3),
    random.uniform(0.7, 1.2),
    random.uniform(0.9, 1.4)
))
bpy.ops.object.mode_set(mode='OBJECT')

# Create a noise texture for displacement
noise_texture = bpy.data.textures.new("RockNoise", type='CLOUDS')
noise_texture.cloud_type = 'COLOR'
noise_texture.noise_scale = 2.5
noise_texture.noise_basis = 'PERLIN'

# Add Displace modifier
displace_mod = obj.modifiers.new(name="Displace", type='DISPLACE')
displace_mod.texture = noise_texture
displace_mod.strength = 0.3
displace_mod.mid_level = 0.5

# Add second noise texture for more variation
noise_texture2 = bpy.data.textures.new("RockNoise2", type='CLOUDS')
noise_texture2.cloud_type = 'COLOR'
noise_texture2.noise_scale = 5.0
noise_texture2.noise_basis = 'PERLIN'

# Add second Displace modifier with different settings
displace_mod2 = obj.modifiers.new(name="Displace2", type='DISPLACE')
displace_mod2.texture = noise_texture2
displace_mod2.strength = 0.15
displace_mod2.mid_level = 0.5

# Apply modifiers to bake the displacement into geometry
bpy.context.view_layer.objects.active = obj
bpy.ops.object.modifier_apply(modifier=displace_mod.name)
bpy.ops.object.modifier_apply(modifier=displace_mod2.name)

# Add slight smoothing with Smooth modifier for natural look
smooth_mod = obj.modifiers.new(name="Smooth", type='SMOOTH')
smooth_mod.factor = 0.2
smooth_mod.iterations = 2

# Apply smoothing
bpy.ops.object.modifier_apply(modifier=smooth_mod.name)

# Final face count
mesh = obj.data
final_face_count = len(mesh.polygons)
print(f"Final face count: {final_face_count}")

# Ensure we're in object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Select the rock for visibility
obj.select_set(True)
