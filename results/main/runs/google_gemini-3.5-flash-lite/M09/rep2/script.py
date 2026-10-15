import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Create an icosphere with 4 subdivisions
# An icosphere with radius 1.0 and 4 subdivisions yields 5120 faces,
# which sits comfortably inside the 2,000 - 60,000 face count range.
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=4,
    radius=1.0,
    location=(0, 0, 0)
)
rock = bpy.context.active_object
rock.name = "NaturalRock"

# 3. Apply irregular non-uniform scale to the object base
rock.scale = (1.2, 0.8, 1.6)

# Apply the scale so modifiers operate in local coordinates predictably
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 4. Create and assign a procedural Noise texture for displacement
noise_texture = bpy.data.textures.new(name="RockNoise", type='NOISE')
noise_texture.noise_scale = 0.8
noise_texture.noise_depth = 4
noise_texture.turbulence = 5.0

# 5. Add a Displace modifier driven by the noise texture
displace_mod = rock.modifiers.new(name="RockDisplace", type='DISPLACE')
displace_mod.texture = noise_texture
displace_mod.strength = 0.35
displace_mod.mid_level = 0.5

# 6. Smooth the geometry out to enhance the organic rock feel
subsurf_mod = rock.modifiers.new(name="RockSubsurf", type='SUBSURF')
subsurf_mod.levels = 1
subsurf_mod.render_levels = 1

# Optional: Add a smooth modifier with a low factor to soften harsh noise peaks
smooth_mod = rock.modifiers.new(name="RockSmooth", type='SMOOTH')
smooth_mod.factor = 0.5
smooth_mod.iterations = 2

# Set shading to smooth for the rock object
for polygon in rock.data.polygons:
    polygon.use_smooth = True
