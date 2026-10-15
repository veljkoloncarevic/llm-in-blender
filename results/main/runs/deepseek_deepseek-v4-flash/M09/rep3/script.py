import bpy

# Ensure object mode and delete any existing objects
try:
    bpy.ops.object.mode_set(mode='OBJECT')
except Exception:
    pass
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a subdivided icosphere (5 subdivisions -> 20,480 faces)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1, location=(0, 0, 0))
rock = bpy.context.active_object
rock.name = "Rock"
rock.data.name = "RockMesh"

# Irregular non-uniform scale for a natural, irregular silhouette
rock.scale = (1.35, 0.8, 1.1)

# Create a procedural noise texture for displacement
noise_tex = bpy.data.textures.new("RockNoise", type='NOISE')
noise_tex.noise_scale = 0.6
noise_tex.noise_depth = 5

# Add a Displace modifier using the noise texture
disp = rock.modifiers.new("RockDisplace", type='DISPLACE')
disp.texture = noise_tex
disp.texture_coords = 'OBJECT'
disp.texture_coords_object = rock
disp.strength = 0.8
disp.mid_level = 0.5

# Smooth shading for a more rock-like appearance
for poly in rock.data.polygons:
    poly.use_smooth = True
