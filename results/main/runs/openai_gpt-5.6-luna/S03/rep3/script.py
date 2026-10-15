import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create Suzanne
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
suzanne = bpy.context.active_object
suzanne.name = "Suzanne"

# Smooth shading
for polygon in suzanne.data.polygons:
    polygon.use_smooth = True

# Add subdivision for a smoother sculpture
subdivision = suzanne.modifiers.new(name="Subdivision Surface", type='SUBSURF')
subdivision.levels = 2
subdivision.render_levels = 2

# Create white marble material
material = bpy.data.materials.new(name="White Marble")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new(type='ShaderNodeOutputMaterial')
output.name = "Material Output"
output.location = (600, 0)

principled = nodes.new(type='ShaderNodeBsdfPrincipled')
principled.name = "Marble Principled BSDF"
principled.location = (300, 0)
principled.inputs["Roughness"].default_value = 0.28
principled.inputs["Specular IOR Level"].default_value = 0.35

tex_coord = nodes.new(type='ShaderNodeTexCoord')
tex_coord.name = "Generated Coordinates"
tex_coord.location = (-800, 0)

noise = nodes.new(type='ShaderNodeTexNoise')
noise.name = "Marble Noise"
noise.location = (-600, 0)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 4.5
noise.inputs["Detail"].default_value = 8.0
noise.inputs["Roughness"].default_value = 0.72
noise.inputs["Distortion"].default_value = 0.35

ramp = nodes.new(type='ShaderNodeValToRGB')
ramp.name = "White Marble Color Ramp"
ramp.location = (-100, 0)

ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
dark = ramp.color_ramp.elements[0]
dark.position = 0.38
dark.color = (0.06, 0.07, 0.075, 1.0)

light = ramp.color_ramp.elements.new(0.52)
light.color = (0.82, 0.84, 0.86, 1.0)

white = ramp.color_ramp.elements.new(0.68)
white.color = (1.0, 1.0, 1.0, 1.0)

ramp.color_ramp.interpolation = 'EASE'

links.new(tex_coord.outputs["Generated"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

suzanne.data.materials.append(material)

# Set a clean object transform
suzanne.location = (0, 0, 0)
suzanne.rotation_euler = (0, 0, 0)
suzanne.scale = (1, 1, 1)
