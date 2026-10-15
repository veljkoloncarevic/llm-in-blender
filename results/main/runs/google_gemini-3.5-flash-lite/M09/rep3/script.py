import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create base icosphere (subdivision 4 yields 2560 faces, which is safely in the 2k-60k range)
bpy.ops.mesh.primitive_icosphere_add(
    subdivisions=4,
    radius=1.0,
    location=(0, 0, 0)
)
rock_obj = bpy.context.active_object
rock_obj.name = "Natural_Rock"

# 2. Apply non-uniform irregular scale
rock_obj.scale = (1.2, 0.8, 1.6)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# 3. Create a procedural noise texture for displacement
noise_tex = bpy.data.textures.new(name="RockNoise", type='STUCCI')
noise_tex.noise_basis = 'BLENDER_ORIGINAL'
noise_tex.noise_type = 'SOFT_NOISE'
noise_tex.noise_scale = 0.6
noise_tex.turbulence = 5.0

# 4. Add a Displace modifier driven by the noise texture
disp_mod = rock_obj.modifiers.new(name="RockDisplace", type='DISPLACE')
disp_mod.texture = noise_tex
disp_mod.strength = 0.35
disp_mod.direction = 'NORMAL'

# 5. Add a Subdivision Surface modifier after displacement to smooth high-frequency details
subsurf_mod = rock_obj.modifiers.new(name="RockSubsurf", type='SUBSURF')
subsurf_mod.levels = 1
subsurf_mod.render_levels = 1

# 6. Smooth shading for a natural rock appearance
bpy.ops.object.shade_smooth()
