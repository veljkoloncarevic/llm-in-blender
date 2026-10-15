import bpy
import bmesh
import mathutils
import random

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4-subdivision icosphere (20 * 4^4 = 5120 faces)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0, location=(0, 0, 0))
rock = bpy.context.active_object
rock.name = "Rock"

# Ensure we're in object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Create a noise-based texture
noise_tex = bpy.data.textures.new("RockNoise", type='NOISE')
noise_tex.noise_scale = 0.6
noise_tex.noise_depth = 4
noise_tex.noise_basis = 'BLENDER'

# Add and configure a Displace modifier
displace = rock.modifiers.new(name="RockDisplace", type='DISPLACE')
displace.texture = noise_tex
displace.strength = 0.7
displace.mid_level = 0.5

# Apply irregular non-uniform scale
rock.scale = (1.0, 0.7, 1.4)

# Verify face count is within allowed range (should be 5120)
face_count = len(rock.data.polygons)
assert 2000 <= face_count <= 60000, f"Face count {face_count} out of range"
