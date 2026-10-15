import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=96,
    radius=1.0,
    depth=2.8,
    end_fill_type='NGON',
    location=(0.0, 0.0, 0.0)
)
cylinder = bpy.context.object
cylinder.name = "Rusty Metal Cylinder"

# Smooth shading
for polygon in cylinder.data.polygons:
    polygon.use_smooth = True

# Beveled edges
bevel = cylinder.modifiers.new(name="Softened Metal Edges", type='BEVEL')
bevel.width = 0.06
bevel.segments = 3
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
mix_shader.name = "Rust Surface Mix"
mix_shader.location = (430, 0)

metal_shader = nodes.new("ShaderNodeBsdfPrincipled")
metal_shader.name = "Grey Metallic Surface"
metal_shader.location = (100, 130)
metal_shader.inputs["Base Color"].default_value = (0.22, 0.25, 0.27, 1.0)
metal_shader.inputs["Metallic"].default_value = 0.92
metal_shader.inputs["Roughness"].default_value = 0.28

rust_shader = nodes.new("ShaderNodeBsdfPrincipled")
rust_shader.name = "Orange Brown Rust Surface"
rust_shader.location = (100, -130)
rust_shader.inputs["Base Color"].default_value = (0.42, 0.075, 0.018, 1.0)
rust_shader.inputs["Metallic"].default_value = 0.05
rust_shader.inputs["Roughness"].default_value = 0.88

texture_coord = nodes.new("ShaderNodeTexCoord")
texture_coord.name = "Generated Coordinates"
texture_coord.location = (-800, 0)

noise = nodes.new("ShaderNodeTexNoise")
noise.name = "Rust Noise Mask"
noise.location = (-600, 80)
noise.noise_dimensions = '3D'
noise.inputs["Scale"].default_value = 4.2
noise.inputs["Detail"].default_value = 6.0
noise.inputs["Roughness"].default_value = 0.78
noise.inputs["Distortion"].default_value = 0.35

ramp = nodes.new("ShaderNodeValToRGB")
ramp.name = "Rust Coverage Control"
ramp.location = (-350, 80)
ramp.color_ramp.interpolation = 'EASE'
ramp.color_ramp.elements[0].position = 0.38
ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
ramp.color_ramp.elements[1].position = 0.60
ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)

bump = nodes.new("ShaderNodeBump")
bump.name = "Corroded Surface Bump"
bump.location = (-80, -330)
bump.inputs["Strength"].default_value = 0.22
bump.inputs["Distance"].default_value = 0.075
bump.inputs["Invert"].default_value = False

# Connect coordinates and procedural mask
links.new(texture_coord.outputs["Generated"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], mix_shader.inputs[0])

# Connect shaders and output
links.new(metal_shader.outputs["BSDF"], mix_shader.inputs[1])
links.new(rust_shader.outputs["BSDF"], mix_shader.inputs[2])
links.new(mix_shader.outputs["Shader"], output.inputs["Surface"])

# Use the noise pattern for surface corrosion
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], metal_shader.inputs["Normal"])
links.new(bump.outputs["Normal"], rust_shader.inputs["Normal"])

# Assign material
cylinder.data.materials.append(material)

# Keep the cylinder selected and active
bpy.context.view_layer.objects.active = cylinder
cylinder.select_set(True)
