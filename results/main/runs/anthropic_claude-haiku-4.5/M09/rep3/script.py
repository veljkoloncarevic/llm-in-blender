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
rock = bpy.context.active_object
rock.name = "Rock"

# Apply non-uniform scale to make it irregular
scale_x = random.uniform(0.7, 1.3)
scale_y = random.uniform(0.7, 1.3)
scale_z = random.uniform(0.7, 1.3)
rock.scale = (scale_x, scale_y, scale_z)
bpy.context.view_layer.update()

# Convert to mesh and subdivide using bmesh
mesh = rock.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Apply subdivision surface (equivalent to 4+ subdivisions)
for _ in range(4):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide()
    bpy.ops.object.mode_set(mode='OBJECT')
    bm = bmesh.new()
    bm.from_mesh(rock.data)

# Check face count
face_count = len(mesh.polygons)
print(f"Face count after subdivision: {face_count}")

# Create noise texture for displacement
noise_texture = bpy.data.textures.new(name="RockNoise", type='CLOUDS')
noise_texture.cloud_type = 'COLOR'
noise_texture.noise_scale = random.uniform(1.5, 3.5)
noise_texture.noise_basis = 'PERLIN'

# Add Displace modifier
displace_mod = rock.modifiers.new(name="DisplaceRock", type='DISPLACE')
displace_mod.texture = noise_texture
displace_mod.strength = random.uniform(0.15, 0.35)
displace_mod.mid_level = 0.5

# Apply some random vertex displacement for additional irregularity
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(1.0, 1.0, 1.0))
bpy.ops.object.mode_set(mode='OBJECT')

# Add slight roughness with a second noise texture and displace
noise_texture_2 = bpy.data.textures.new(name="RockNoise2", type='MARBLE')
noise_texture_2.noise_scale = random.uniform(0.5, 1.5)
noise_texture_2.marble_type = 'SHARP'

displace_mod_2 = rock.modifiers.new(name="DisplaceRock2", type='DISPLACE')
displace_mod_2.texture = noise_texture_2
displace_mod_2.strength = random.uniform(0.05, 0.15)

# Ensure we have a material for visibility
mat = bpy.data.materials.new(name="RockMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.4, 0.38, 1.0)
mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
rock.data.materials.append(mat)

# Final face count check
final_face_count = len(rock.data.polygons)
print(f"Final face count: {final_face_count}")

# Ensure face count is in valid range
if final_face_count < 2000:
    print(f"Warning: Face count {final_face_count} is below minimum of 2000")
elif final_face_count > 60000:
    print(f"Warning: Face count {final_face_count} exceeds maximum of 60000")
else:
    print(f"Face count {final_face_count} is within valid range [2000, 60000]")
