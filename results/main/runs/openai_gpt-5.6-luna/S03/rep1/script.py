import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create Suzanne
bpy.ops.mesh.primitive_monkey_add(location=(0.0, 0.0, 0.0))
suzanne = bpy.context.active_object
suzanne.name = "Marble Suzanne"

# Smooth shading
for polygon in suzanne.data.polygons:
    polygon.use_smooth = True

# Add subdivision for a smoother sculptural form
subdivision = suzanne.modifiers.new(name="Subdivision Surface", type='SUBSURF')
subdivision.subdivision_type = 'CATMULL_CLARK'
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

noise = nodes.new(type='ShaderNodeTexNoise')
noise.name = "Marble Noise"
noise.location = (-600, 0)
noise.inputs["Scale"].default_value = 5.0
noise.inputs["Detail"].default_value = 7.0
noise.inputs["Roughness"].default_value = 0.65
noise.inputs["Distortion"].default_value = 0.35

ramp = nodes.new(type='ShaderNodeValToRGB')
ramp.name = "Marble Color Ramp"
ramp.location = (-150, 0)

ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
dark = ramp.color_ramp.elements[0]
dark.position = 0.32
dark.color = (0.18, 0.20, 0.22, 1.0)

mid = ramp.color_ramp.elements.new(0.47)
mid.color = (0.62, 0.65, 0.68, 1.0)

light = ramp.color_ramp.elements.new(0.58)
light.color = (0.96, 0.97, 0.98, 1.0)

white = ramp.color_ramp.elements.new(0.78)
white.color = (1.0, 1.0, 1.0, 1.0)

links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], principled.inputs["Base Color"])
links.new(principled.outputs["BSDF"], output.inputs["Surface"])

suzanne.data.materials.append(material)

# Frame the object in the viewport
bpy.context.view_layer.objects.active = suzanne
suzanne.select_set(True)
