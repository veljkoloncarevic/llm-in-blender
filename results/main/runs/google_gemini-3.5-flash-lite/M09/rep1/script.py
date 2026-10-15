import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create base icosphere (subdivisions = 4 yields 5,120 faces, which is within the 2,000 - 60,000 range)
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=4,
    radius=1.0,
    location=(0, 0, 0)
)
rock = bpy.context.active_object
rock.name = "NaturalRock"

# Apply irregular non-uniform scale to the object to make it elongated/rock-like
rock.scale = (1.2, 0.8, 1.6)

# 2. Create a procedural noise texture for displacement
noise_texture = bpy.data.textures.new(name="RockNoise", type='NOISE')
noise_texture.noise_scale = 0.8
noise_texture.noise_depth = 4
noise_texture.turbulence = 5.0

# 3. Add a Displace modifier driven by the noise texture
displace_mod = rock.modifiers.new(name="RockDisplace", type='DISPLACE')
displace_mod.texture = noise_texture
displace_mod.strength = 0.35
displace_mod.direction = 'NORMAL'

# 4. Add a Subdivision Surface modifier for extra organic smoothness and density
subsurf_mod = rock.modifiers.new(name="RockSubsurf", type='SUBSURF')
subsurf_mod.levels = 1
subsurf_mod.render_levels = 1

# Optional: Set smooth shading for all faces
for poly in rock.data.polygons:
    poly.use_smooth = True

# Ensure the object is active and selected
bpy.context.view_layer.objects.active = rock
rock.select_set(True)
