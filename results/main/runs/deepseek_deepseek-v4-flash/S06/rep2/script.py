import bpy
import math

# Remove all existing objects
if bpy.context.object:
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a wooden plank mesh (4 x 0.4 x 0.1)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
plank = bpy.context.active_object
plank.scale = (2.0, 0.2, 0.05)
bpy.ops.object.transform_apply(scale=True)
plank.name = "WoodenPlank"

# Build procedural wood material
mat = bpy.data.materials.new("WoodMaterial")
mat.use_nodes = True
ntree = mat.node_tree
ntree.nodes.clear()

nodes = ntree.nodes
links = ntree.links

output = nodes.new(type='ShaderNodeOutputMaterial')
principled = nodes.new(type='ShaderNodeBsdfPrincipled')
tex_coord = nodes.new(type='ShaderNodeTexCoord')
mapping = nodes.new(type='ShaderNodeMapping')
noise = nodes.new(type='ShaderNodeTexNoise')
wave = nodes.new(type='ShaderNodeTexWave')
color_ramp = nodes.new(type='ShaderNodeValToRGB')
rgb_to_bw = nodes.new(type='ShaderNodeRGBToBW')
bump = nodes.new(type='ShaderNodeBump')

# Orient grain along the length of the plank
mapping.rotation = (0.0, 0.0, math.pi / 2.0)
mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)

wave.wave_type = 'BANDS'
wave.inputs["Scale"].default_value = 5.0
wave.inputs["Distortion"].default_value = 2.0

noise.inputs["Scale"].default_value = 3.0
noise.inputs["Detail"].default_value = 2.0
noise.inputs["Roughness"].default_value = 0.5

# Brown wood color ramp
color_ramp.color_ramp.elements[0].color = (0.15, 0.08, 0.04, 1.0)
color_ramp.color_ramp.elements[0].position = 0.0
color_ramp.color_ramp.elements[1].color = (0.7, 0.5, 0.3, 1.0)
color_ramp.color_ramp.elements[1].position = 1.0

bump.inputs["Strength"].default_value = 0.2
principled.inputs["Roughness"].default_value = 0.6

# Connections
links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])
links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
links.new(mapping.outputs["Vector"], wave.inputs["Vector"])

links.new(noise.outputs["Fac"], wave.inputs["Distortion"])

links.new(wave.outputs["Fac"], color_ramp.inputs["Fac"])
links.new(color_ramp.outputs["Color"], principled.inputs["Base Color"])

links.new(color_ramp.outputs["Color"], rgb_to_bw.inputs["Color"])
links.new(rgb_to_bw.outputs["Val"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], principled.inputs["Normal"])

links.new(principled.outputs["BSDF"], output.inputs["Surface"])

plank.data.materials.append(mat)
