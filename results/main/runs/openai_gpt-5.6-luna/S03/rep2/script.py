import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Add Suzanne
bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
suzanne = bpy.context.object
suzanne.name = "Suzanne"

# Smooth shading
for polygon in suzanne.data.polygons:
    polygon.use_smooth = True

# Add subdivision for a smoother marble surface
subsurf = suzanne.modifiers.new(name="Subdivision Surface", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

# Create white marble material
material = bpy.data.materials.new(name="White Marble")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new(type="ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (600, 0)

bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
bsdf.name = "Marble Principled BSDF"
bsdf.location = (300, 0)
bsdf.inputs["Roughness"].default_value = 0.28
bsdf.inputs["Specular IOR Level"].default_value = 0.35

texcoord = nodes.new(type="ShaderNodeTexCoord")
texcoord.name = "Texture Coordinates"
texcoord.location = (-800, 0)

noise = nodes.new(type="ShaderNodeTexNoise")
noise.name = "Marble Noise"
noise.location = (-600, 0)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 5.0
noise.inputs["Detail"].default_value = 7.0
noise.inputs["Roughness"].default_value = 0.7
noise.inputs["Distortion"].default_value = 0.2

ramp = nodes.new(type="ShaderNodeValToRGB")
ramp.name = "White Marble Color Ramp"
ramp.location = (-200, 0)
ramp.color_ramp.interpolation = 'EASE'
ramp.color_ramp.elements[0].position = 0.28
ramp.color_ramp.elements[0].color = (0.08, 0.08, 0.08, 1.0)
ramp.color_ramp.elements[1].position = 0.72
ramp.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1.0)

links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

suzanne.data.materials.append(material)

# Set a useful viewport color
material.diffuse_color = (0.8, 0.8, 0.8, 1.0)
