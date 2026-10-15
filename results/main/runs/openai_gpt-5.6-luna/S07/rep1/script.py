import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=96,
    radius=1.0,
    depth=3.0,
    location=(0.0, 0.0, 0.0)
)
cylinder = bpy.context.object
cylinder.name = "Rusty Metal Cylinder"

# Smooth shading
for polygon in cylinder.data.polygons:
    polygon.use_smooth = True

# Slightly round the cylinder edges
bevel = cylinder.modifiers.new(name="Rounded Edges", type='BEVEL')
bevel.width = 0.08
bevel.segments = 3
bevel.limit_method = 'ANGLE'

# Create the material
material = bpy.data.materials.new(name="Rusty Metal")
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

metal_shader = nodes.new("ShaderNodeBsdfPrincipled")
metal_shader.name = "Grey Metallic Surface"
metal_shader.location = (100, 130)
metal_shader.inputs["Base Color"].default_value = (0.22, 0.25, 0.27, 1.0)
metal_shader.inputs["Metallic"].default_value = 0.88
metal_shader.inputs["Roughness"].default_value = 0.28

rust_shader = nodes.new("ShaderNodeBsdfPrincipled")
rust_shader.name = "Orange Brown Rust Surface"
rust_shader.location = (100, -130)
rust_shader.inputs["Base Color"].default_value = (0.42, 0.095, 0.025, 1.0)
rust_shader.inputs["Metallic"].default_value = 0.08
rust_shader.inputs["Roughness"].default_value = 0.86

texcoord = nodes.new("ShaderNodeTexCoord")
texcoord.name = "Generated Coordinates"
texcoord.location = (-700, 0)

noise = nodes.new("ShaderNodeTexNoise")
noise.name = "Rust Mask Noise"
noise.location = (-500, 0)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 3.6
noise.inputs["Detail"].default_value = 6.0
noise.inputs["Roughness"].default_value = 0.72
noise.inputs["Distortion"].default_value = 0.25

ramp = nodes.new("ShaderNodeValToRGB")
ramp.name = "Rust Coverage Mask"
ramp.location = (-220, -20)
ramp.color_ramp.interpolation = 'EASE'
ramp.color_ramp.elements[0].position = 0.40
ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp.color_ramp.elements[1].position = 0.60
ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

bump = nodes.new("ShaderNodeBump")
bump.name = "Rust Surface Bump"
bump.location = (100, -330)
bump.inputs["Strength"].default_value = 0.22
bump.inputs["Distance"].default_value = 0.08

# Connect procedural texture and shaders
links.new(texcoord.outputs["Generated"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], mix_shader.inputs[0])
links.new(metal_shader.outputs["BSDF"], mix_shader.inputs[1])
links.new(rust_shader.outputs["BSDF"], mix_shader.inputs[2])
links.new(mix_shader.outputs["Shader"], output.inputs["Surface"])
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], metal_shader.inputs["Normal"])
links.new(bump.outputs["Normal"], rust_shader.inputs["Normal"])

# Assign the material
cylinder.data.materials.append(material)

# Set a useful viewport display color
material.diffuse_color = (0.30, 0.12, 0.045, 1.0)

# Keep the cylinder selected and active
bpy.context.view_layer.objects.active = cylinder
cylinder.select_set(True)
