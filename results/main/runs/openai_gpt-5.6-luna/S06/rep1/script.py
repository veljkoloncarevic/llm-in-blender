import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the wooden plank from a scaled cube
bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
plank = bpy.context.object
plank.name = "Wooden_Plank"
plank.scale = (4.0, 1.25, 0.2)

# Slightly soften the plank edges
bevel = plank.modifiers.new(name="Softened Edges", type='BEVEL')
bevel.width = 0.08
bevel.segments = 3

# Create the procedural wood material
material = bpy.data.materials.new(name="Procedural Wood")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (700, 0)

principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.name = "Wood Principled BSDF"
principled.location = (400, 0)
principled.inputs["Roughness"].default_value = 0.42

texcoord = nodes.new("ShaderNodeTexCoord")
texcoord.name = "Generated Coordinates"
texcoord.location = (-900, 50)

mapping = nodes.new("ShaderNodeMapping")
mapping.name = "Wood Grain Mapping"
mapping.location = (-700, 50)
mapping.inputs["Scale"].default_value = (1.0, 5.0, 18.0)

noise = nodes.new("ShaderNodeTexNoise")
noise.name = "Wood Distortion Noise"
noise.location = (-480, -180)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 2.8
noise.inputs["Detail"].default_value = 5.0
noise.inputs["Roughness"].default_value = 0.7

wave = nodes.new("ShaderNodeTexWave")
wave.name = "Wood Grain Wave"
wave.location = (-220, 100)
wave.wave_type = 'BANDS'
wave.bands_direction = 'Y'
wave.inputs["Scale"].default_value = 4.5
wave.inputs["Distortion"].default_value = 3.0
wave.inputs["Detail"].default_value = 5.0
wave.inputs["Detail Scale"].default_value = 2.0
wave.inputs["Roughness"].default_value = 0.7

ramp = nodes.new("ShaderNodeValToRGB")
ramp.name = "Brown Wood Color Ramp"
ramp.location = (20, 100)
ramp.color_ramp.interpolation = 'EASE'

ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
dark = ramp.color_ramp.elements[0]
dark.position = 0.22
dark.color = (0.025, 0.006, 0.002, 1.0)

mid = ramp.color_ramp.elements.new(0.42)
mid.color = (0.16, 0.035, 0.012, 1.0)

light = ramp.color_ramp.elements.new(0.68)
light.color = (0.42, 0.12, 0.035, 1.0)

highlight = ramp.color_ramp.elements.new(0.86)
highlight.color = (0.72, 0.30, 0.085, 1.0)

bump = nodes.new("ShaderNodeBump")
bump.name = "Wood Grain Bump"
bump.location = (190, -150)
bump.inputs["Strength"].default_value = 0.32
bump.inputs["Distance"].default_value = 0.12

links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
links.new(noise.outputs["Fac"], wave.inputs["Distortion"])
links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
links.new(ramp.outputs["Color"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

plank.data.materials.append(material)

# Set a useful viewport display color
material.diffuse_color = (0.36, 0.09, 0.025, 1.0)
