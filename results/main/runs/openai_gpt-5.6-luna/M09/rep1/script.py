import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (
    bpy.data.meshes,
    bpy.data.curves,
    bpy.data.materials,
    bpy.data.cameras,
    bpy.data.lights,
):
    for datablock in list(datablocks):
        if datablock.users == 0:
            datablocks.remove(datablock)

# Create a high-resolution icosphere
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=4,
    radius=1.0,
    location=(0.0, 0.0, 0.0)
)
rock = bpy.context.active_object
rock.name = "Natural_Noise_Deformed_Rock"

# Irregular non-uniform proportions and orientation
rock.scale = (1.45, 1.12, 0.86)
rock.rotation_euler = (
    math.radians(-7.0),
    math.radians(11.0),
    math.radians(23.0),
)

# Noise texture for the displacement modifier
noise_texture = bpy.data.textures.new(
    name="Rock_Fractal_Noise",
    type='CLOUDS'
)
noise_texture.noise_scale = 0.42
noise_texture.noise_depth = 3
noise_texture.noise_type = 'SOFT_NOISE'
noise_texture.noise_basis = 'IMPROVED_PERLIN'

# Primary natural surface deformation
displace = rock.modifiers.new(
    name="Natural_Rock_Displacement",
    type='DISPLACE'
)
displace.texture = noise_texture
displace.texture_coords = 'LOCAL'
displace.strength = 0.34
displace.mid_level = 0.50

# Slight additional broad-form variation using a second noise scale
broad_texture = bpy.data.textures.new(
    name="Rock_Broad_Form_Noise",
    type='CLOUDS'
)
broad_texture.noise_scale = 0.95
broad_texture.noise_depth = 2
broad_texture.noise_type = 'SOFT_NOISE'
broad_texture.noise_basis = 'IMPROVED_PERLIN'

broad_displace = rock.modifiers.new(
    name="Broad_Rock_Form",
    type='DISPLACE'
)
broad_displace.texture = broad_texture
broad_displace.texture_coords = 'LOCAL'
broad_displace.strength = 0.12
broad_displace.mid_level = 0.52

# Smooth shading while preserving the faceted silhouette
for polygon in rock.data.polygons:
    polygon.use_smooth = True

# Rock material
material = bpy.data.materials.new(name="Weathered_Rock_Material")
material.diffuse_color = (0.22, 0.19, 0.15, 1.0)
material.use_nodes = True

principled = material.node_tree.nodes.get("Principled BSDF")
if principled:
    principled.inputs["Base Color"].default_value = (0.22, 0.19, 0.15, 1.0)
    principled.inputs["Roughness"].default_value = 0.88
    principled.inputs["Specular IOR Level"].default_value = 0.22

rock.data.materials.append(material)

# Display settings
rock.show_name = True
rock.color = (0.22, 0.19, 0.15, 1.0)

# Ensure the rock is the active selected object
bpy.context.view_layer.objects.active = rock
rock.select_set(True)
