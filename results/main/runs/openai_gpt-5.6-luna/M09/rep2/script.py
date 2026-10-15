import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a high-resolution icosphere
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=5,
    radius=1.0,
    location=(0.0, 0.0, 0.0)
)
rock = bpy.context.active_object
rock.name = "Natural_Rock"

# Irregular non-uniform scale and slight rotation
rock.scale = (1.35, 1.05, 0.78)
rock.rotation_euler = (
    math.radians(-7.0),
    math.radians(11.0),
    math.radians(18.0),
)

# Noise texture for displacement
noise_texture = bpy.data.textures.new(
    name="Rock_Noise",
    type='CLOUDS'
)
noise_texture.noise_scale = 0.58
noise_texture.noise_depth = 3
noise_texture.noise_type = 'SOFT_NOISE'
noise_texture.contrast = 1.35
noise_texture.intensity = 1.0

# Primary natural rock displacement
displace = rock.modifiers.new(name="Natural Noise Displacement", type='DISPLACE')
displace.texture = noise_texture
displace.texture_coords = 'GLOBAL'
displace.strength = 0.32
displace.mid_level = 0.48

# Add subtle secondary variation using the same noise-driven displacement
fine_texture = bpy.data.textures.new(
    name="Fine_Rock_Noise",
    type='CLOUDS'
)
fine_texture.noise_scale = 0.18
fine_texture.noise_depth = 2
fine_texture.noise_type = 'SOFT_NOISE'
fine_texture.contrast = 1.2

fine_displace = rock.modifiers.new(name="Fine Surface Variation", type='DISPLACE')
fine_displace.texture = fine_texture
fine_displace.texture_coords = 'GLOBAL'
fine_displace.strength = 0.055
fine_displace.mid_level = 0.5

# Slightly flatten the underside for a naturally resting rock
mesh = rock.data
for vertex in mesh.vertices:
    if vertex.co.z < -0.72:
        factor = max(0.0, min(1.0, (-vertex.co.z - 0.72) / 0.28))
        vertex.co.z = vertex.co.z * (1.0 - factor) + (-0.72) * factor

# Smooth shading while preserving the irregular silhouette
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Rock material
material = bpy.data.materials.new(name="Rock Material")
material.diffuse_color = (0.22, 0.19, 0.15, 1.0)
material.roughness = 0.92
material.metallic = 0.0
rock.data.materials.append(material)

# Ensure the object is active and selected
bpy.context.view_layer.objects.active = rock
rock.select_set(True)
