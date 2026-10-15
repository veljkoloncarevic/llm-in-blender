import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=96,
    radius=1.0,
    depth=3.2,
    location=(0.0, 0.0, 1.6)
)
cylinder = bpy.context.object
cylinder.name = "Rusty Metal Cylinder"

# Smooth shading
for polygon in cylinder.data.polygons:
    polygon.use_smooth = True

# Beveled edges
bevel = cylinder.modifiers.new(name="Softened Edges", type='BEVEL')
bevel.width = 0.08
bevel.segments = 4
bevel.limit_method = 'ANGLE'

# Create rusty metal material
material = bpy.data.materials.new(name="Procedural Rusty Metal")
material.use_nodes = True
nodes = material.node_tree.nodes
links = material.node_tree.links
nodes.clear()

output = nodes.new("ShaderNodeOutputMaterial")
output.name = "Material Output"
output.location = (700, 0)

mix_shader = nodes.new("ShaderNodeMixShader")
mix_shader.name = "Rust and Metal Mix"
mix_shader.location = (450, 0)

metal = nodes.new("ShaderNodeBsdfPrincipled")
metal.name = "Grey Metallic Surface"
metal.location = (100, 130)
metal.inputs["Base Color"].default_value = (0.24, 0.27, 0.29, 1.0)
metal.inputs["Metallic"].default_value = 0.92
metal.inputs["Roughness"].default_value = 0.28

rust = nodes.new("ShaderNodeBsdfPrincipled")
rust.name = "Orange Brown Rust Surface"
rust.location = (100, -150)
rust.inputs["Base Color"].default_value = (0.48, 0.105, 0.025, 1.0)
rust.inputs["Metallic"].default_value = 0.08
rust.inputs["Roughness"].default_value = 0.88

noise = nodes.new("ShaderNodeTexNoise")
noise.name = "Rust Pattern Noise"
noise.location = (-500, 50)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 4.2
noise.inputs["Detail"].default_value = 5.0
noise.inputs["Roughness"].default_value = 0.72
noise.inputs["Lacunarity"].default_value = 2.0

ramp = nodes.new("ShaderNodeValToRGB")
ramp.name = "Rust Mask"
ramp.location = (-250, 100)
ramp.color_ramp.interpolation = 'EASE'
ramp.color_ramp.elements[0].position = 0.40
ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp.color_ramp.elements[1].position = 0.60
ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

bump = nodes.new("ShaderNodeBump")
bump.name = "Corroded Surface Bump"
bump.location = (-40, -330)
bump.inputs["Strength"].default_value = 0.24
bump.inputs["Distance"].default_value = 0.10

# Add a second subtle noise layer for surface breakup
fine_noise = nodes.new("ShaderNodeTexNoise")
fine_noise.name = "Fine Corrosion Detail"
fine_noise.location = (-500, -280)
fine_noise.noise_dimensions = '3D'
fine_noise.inputs["Scale"].default_value = 18.0
fine_noise.inputs["Detail"].default_value = 3.0
fine_noise.inputs["Roughness"].default_value = 0.78

mix_detail = nodes.new("ShaderNodeMixRGB")
mix_detail.name = "Combined Surface Detail"
mix_detail.blend_type = 'MULTIPLY'
mix_detail.inputs[0].default_value = 0.35
mix_detail.location = (-250, -220)

# Link procedural texture network
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(noise.outputs["Fac"], mix_detail.inputs[1])
links.new(fine_noise.outputs["Fac"], mix_detail.inputs[2])
links.new(mix_detail.outputs["Color"], bump.inputs["Height"])

# Rust mask controls shader blending
links.new(ramp.outputs["Color"], mix_shader.inputs[0])
links.new(metal.outputs["BSDF"], mix_shader.inputs[1])
links.new(rust.outputs["BSDF"], mix_shader.inputs[2])

# Apply the same corroded normal to both surfaces
links.new(bump.outputs["Normal"], metal.inputs["Normal"])
links.new(bump.outputs["Normal"], rust.inputs["Normal"])
links.new(mix_shader.outputs["Shader"], output.inputs["Surface"])

cylinder.data.materials.append(material)

# Useful viewport appearance
material.diffuse_color = (0.32, 0.12, 0.045, 1.0)
cylinder.show_name = True
