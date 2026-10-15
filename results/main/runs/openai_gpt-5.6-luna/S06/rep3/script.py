import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create the wooden plank from a scaled cube
bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
plank = bpy.context.object
plank.name = "Wooden_Plank"
plank.scale = (3.5, 1.0, 0.18)

# Apply a small bevel for softened plank edges
bevel = plank.modifiers.new(name="Subtle Edge Bevel", type='BEVEL')
bevel.width = 0.06
bevel.segments = 3

# Create the procedural wood material
material = bpy.data.materials.new(name="Procedural Wood")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (800, 0)

principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.name = "Wood Principled BSDF"
principled.location = (520, 0)
principled.inputs["Roughness"].default_value = 0.48

texcoord = nodes.new("ShaderNodeTexCoord")
texcoord.name = "Texture Coordinates"
texcoord.location = (-900, 0)

mapping = nodes.new("ShaderNodeMapping")
mapping.name = "Wood Grain Mapping"
mapping.location = (-700, 0)
mapping.inputs["Scale"].default_value = (1.0, 7.0, 3.0)

noise = nodes.new("ShaderNodeTexNoise")
noise.name = "Wood Distortion Noise"
noise.location = (-480, -180)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 3.2
noise.inputs["Detail"].default_value = 5.0
noise.inputs["Roughness"].default_value = 0.7
noise.inputs["Lacunarity"].default_value = 2.0

wave = nodes.new("ShaderNodeTexWave")
wave.name = "Wood Grain Wave"
wave.location = (-220, 80)
wave.wave_type = 'BANDS'
wave.bands_direction = 'Y'
wave.profile = 'SIN'
wave.inputs["Scale"].default_value = 5.5
wave.inputs["Distortion"].default_value = 6.0
wave.inputs["Detail"].default_value = 5.0
wave.inputs["Detail Scale"].default_value = 2.0
wave.inputs["Detail Roughness"].default_value = 0.7

ramp = nodes.new("ShaderNodeValToRGB")
ramp.name = "Brown Wood Color Ramp"
ramp.location = (40, 100)
ramp.color_ramp.interpolation = 'EASE'

ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])

dark = ramp.color_ramp.elements[0]
dark.position = 0.18
dark.color = (0.035, 0.008, 0.002, 1.0)

mid_dark = ramp.color_ramp.elements.new(0.34)
mid_dark.color = (0.16, 0.045, 0.012, 1.0)

mid = ramp.color_ramp.elements.new(0.55)
mid.color = (0.38, 0.12, 0.035, 1.0)

light = ramp.color_ramp.elements.new(0.76)
light.color = (0.68, 0.29, 0.085, 1.0)

bright = ramp.color_ramp.elements.new(0.91)
bright.color = (0.9, 0.52, 0.2, 1.0)

bump = nodes.new("ShaderNodeBump")
bump.name = "Wood Grain Bump"
bump.location = (280, -150)
bump.inputs["Strength"].default_value = 0.28
bump.inputs["Distance"].default_value = 0.09

links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
links.new(noise.outputs["Fac"], wave.inputs["Distortion"])
links.new(wave.outputs["Color"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
links.new(ramp.outputs["Color"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

plank.data.materials.append(material)
