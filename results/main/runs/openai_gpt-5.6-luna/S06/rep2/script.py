import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the wooden plank from a scaled cube
bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
plank = bpy.context.active_object
plank.name = "Wooden Plank"
plank.scale = (3.5, 0.75, 0.2)

# Beveled edges
bevel = plank.modifiers.new(name="Softened Edges", type='BEVEL')
bevel.width = 0.08
bevel.segments = 3

# Create procedural wood material
material = bpy.data.materials.new(name="Procedural Wood")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (850, 0)

principled = nodes.new("ShaderNodeBsdfPrincipled")
principled.name = "Wood Principled BSDF"
principled.location = (580, 0)
principled.inputs["Roughness"].default_value = 0.48

tex_coord = nodes.new("ShaderNodeTexCoord")
tex_coord.name = "Generated Coordinates"
tex_coord.location = (-850, 0)

mapping = nodes.new("ShaderNodeMapping")
mapping.name = "Wood Mapping"
mapping.location = (-650, 0)
mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)

noise = nodes.new("ShaderNodeTexNoise")
noise.name = "Wood Distortion Noise"
noise.location = (-400, -220)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 4.0
noise.inputs["Detail"].default_value = 5.0
noise.inputs["Roughness"].default_value = 0.7
noise.inputs["Distortion"].default_value = 0.25

wave = nodes.new("ShaderNodeTexWave")
wave.name = "Wood Grain Wave"
wave.location = (-120, 80)
wave.wave_type = 'BANDS'
wave.bands_direction = 'Y'
wave.inputs["Scale"].default_value = 7.0
wave.inputs["Distortion"].default_value = 4.0
wave.inputs["Detail"].default_value = 5.0
wave.inputs["Detail Scale"].default_value = 2.0

ramp = nodes.new("ShaderNodeValToRGB")
ramp.name = "Brown Wood Color Ramp"
ramp.label = "Brown Wood Tones"
ramp.location = (150, 100)

ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
dark = ramp.color_ramp.elements[0]
dark.position = 0.18
dark.color = (0.035, 0.008, 0.002, 1.0)

mid_dark = ramp.color_ramp.elements.new(0.38)
mid_dark.color = (0.16, 0.035, 0.008, 1.0)

mid = ramp.color_ramp.elements.new(0.58)
mid.color = (0.34, 0.11, 0.025, 1.0)

light = ramp.color_ramp.elements.new(0.78)
light.color = (0.62, 0.27, 0.075, 1.0)

highlight = ramp.color_ramp.elements.new(0.94)
highlight.color = (0.82, 0.46, 0.16, 1.0)

bump = nodes.new("ShaderNodeBump")
bump.name = "Wood Grain Bump"
bump.location = (350, -170)
bump.inputs["Strength"].default_value = 0.3
bump.inputs["Distance"].default_value = 0.08

links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
links.new(mapping.outputs["Vector"], wave.inputs["Vector"])
links.new(noise.outputs["Fac"], wave.inputs["Distortion"])
links.new(wave.outputs["Color"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
links.new(ramp.outputs["Color"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

plank.data.materials.append(material)
