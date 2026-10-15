import bpy
import math

# Remove all existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove orphaned mesh and texture datablocks from the previous scene
for datablock in list(bpy.data.meshes):
    if datablock.users == 0:
        bpy.data.meshes.remove(datablock)
for datablock in list(bpy.data.textures):
    if datablock.users == 0:
        bpy.data.textures.remove(datablock)

# Create a dense icosphere: subdivision 5 gives 10,240 triangular faces
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=5,
    radius=1.0,
    location=(0.0, 0.0, 0.0)
)
rock = bpy.context.object
rock.name = "Natural_Rock"

# Irregular non-uniform scale and slight tilt
rock.scale = (1.45, 1.08, 1.22)
rock.rotation_euler = (
    math.radians(-8.0),
    math.radians(13.0),
    math.radians(21.0),
)

# Noise texture for procedural displacement
noise = bpy.data.textures.new("Rock_Surface_Noise", type='CLOUDS')
noise.noise_scale = 0.48
noise.noise_depth = 3
noise.contrast = 1.35
noise.noise_type = 'SOFT_NOISE'
noise.noise_basis = 'IMPROVED_PERLIN'

# Displace the icosphere along its normals
displace = rock.modifiers.new("Natural_Irregular_Displacement", type='DISPLACE')
displace.texture = noise
displace.texture_coords = 'GLOBAL'
displace.direction = 'NORMAL'
displace.strength = 0.34
displace.mid_level = 0.48
displace.vertex_group = ""

# Add a subtle smoothing pass while preserving the displaced silhouette
smooth = rock.modifiers.new("Subtle_Surface_Smoothing", type='SMOOTH')
smooth.factor = 0.18
smooth.iterations = 2

# Smooth shading for a natural rock surface
for polygon in rock.data.polygons:
    polygon.use_smooth = True

# Rock-colored material
material = bpy.data.materials.new("Weathered_Rock_Material")
material.diffuse_color = (0.24, 0.20, 0.15, 1.0)
material.roughness = 0.9
rock.data.materials.append(material)

# Ensure the rock is the active selected object
bpy.context.view_layer.objects.active = rock
rock.select_set(True)
