import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cylinder from scratch
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0, depth=3.0, vertices=32, location=(0, 0, 0)
)
cylinder = bpy.active_object
cylinder.name = "RustyCylinder"

# Smooth shading for the cylinder
for polygon in cylinder.data.polygons:
    polygon.use_smooth = True

# Create a new material for rust and metal blending
mat = bpy.data.materials.new(name="RustyMetalMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# -----------------------------------------------------------------------------
# Create Nodes
# -----------------------------------------------------------------------------

# Output node
node_output = nodes.new(type="ShaderNodeOutputMaterial")
node_output.location = (800, 0)

# Principled BSDF for Metal (Grey, high metallic, low roughness)
node_metal = nodes.new(type="ShaderNodeBsdfPrincipled")
node_metal.name = "Metal_BSDF"
node_metal.location = (200, 200)
node_metal.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)  # Grey
node_metal.inputs["Metallic"].default_value = 1.0
node_metal.inputs["Roughness"].default_value = 0.2

# Principled BSDF for Rust (Orange-Brown, rough, non-metallic)
node_rust = nodes.new(type="ShaderNodeBsdfPrincipled")
node_rust.name = "Rust_BSDF"
node_rust.location = (200, -200)
node_rust.inputs["Base Color"].default_value = (
    0.42,
    0.18,
    0.05,
    1.0,
)  # Orange-Brown
node_rust.inputs["Metallic"].default_value = 0.0
node_rust.inputs["Roughness"].default_value = 0.85

# Mix Shader to blend Metal and Rust
node_mix_shader = nodes.new(type="ShaderNodeMixShader")
node_mix_shader.location = (550, 0)

# Noise Texture to drive the rust mask
node_noise = nodes.new(type="ShaderNodeTexNoise")
node_noise.location = (-300, 0)
node_noise.inputs["Scale"].default_value = 8.0
node_noise.inputs["Detail"].default_value = 4.0
node_noise.inputs["Roughness"].default_value = 0.5

# Color Ramp to control rust distribution (contrast/threshold)
node_ramp = nodes.new(type="ShaderNodeValToRGB")
node_ramp.location = (-50, 0)
# Adjust stops to balance metal vs rust
node_ramp.color_ramp.elements[0].position = 0.35
node_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)  # Metal (Shader 1)
node_ramp.color_ramp.elements[1].position = 0.65
node_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)  # Rust (Shader 2)

# Texture Coordinate and Mapping for proper procedural projection
node_tex_coord = nodes.new(type="ShaderNodeTexCoord")
node_tex_coord.location = (-750, 0)

node_mapping = nodes.new(type="ShaderNodeMapping")
node_mapping.location = (-520, 0)
node_mapping.inputs["Scale"].default_value = (1.5, 1.5, 1.5)

# -----------------------------------------------------------------------------
# Link Nodes
# -----------------------------------------------------------------------------

# Coordinate pipeline
links.new(node_tex_coord.outputs["Object"], node_mapping.inputs["Vector"])
links.new(node_mapping.outputs["Vector"], node_noise.inputs["Vector"])

# Noise to ColorRamp mask
links.new(node_noise.outputs["Fac"], node_ramp.inputs["Fac"])

# Mask (ColorRamp) to Mix Shader factor
links.new(node_ramp.outputs["Color"], node_mix_shader.inputs["Fac"])

# Shaders to Mix Shader
# Shader 1 (Index 0) = Metal
links.new(node_metal.outputs["BSDF"], node_mix_shader.inputs[1])
# Shader 2 (Index 1) = Rust
links.new(node_rust.outputs["BSDF"], node_mix_shader.inputs[2])

# Mix Shader to Material Output
links.new(node_mix_shader.outputs["Shader"], node_output.inputs["Surface"])

# -----------------------------------------------------------------------------
# Assign Material to Cylinder
# -----------------------------------------------------------------------------
if cylinder.data.materials:
    cylinder.data.materials[0] = mat
else:
    cylinder.data.materials.append(mat)
