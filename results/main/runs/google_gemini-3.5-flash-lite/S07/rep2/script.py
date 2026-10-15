import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0, depth=2.5, vertices=64, location=(0, 0, 0)
)
cylinder = bpy.active_object
cylinder.name = "RustyCylinder"

# Smooth shading for the cylinder
for polygon in cylinder.data.polygons:
    polygon.use_smooth = True

# 3. Create the Rusty Metal Material using Nodes
mat = bpy.data.materials.new(name="RustyMetalMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# --- Create Nodes ---

# Output
node_output = nodes.new(type="ShaderNodeOutputMaterial")
node_output.location = (800, 0)

# Principled BSDF (Final Mix Shader output will plug into this, or we mix using Principled BSDF's internal mix)
# Using a dedicated Mix Shader with two Principled BSDFs gives the best metallic/roughness separation.
node_metal_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
node_metal_bsdf.name = "MetalBSDF"
node_metal_bsdf.location = (200, 200)
# Configure Metal base
node_metal_bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)  # Grey metal
node_metal_bsdf.inputs["Metallic"].default_value = 0.95
node_metal_bsdf.inputs["Roughness"].default_value = 0.2

node_rust_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
node_rust_bsdf.name = "RustBSDF"
node_rust_bsdf.location = (200, -200)
# Configure Rust base (orange-brown)
node_rust_bsdf.inputs["Base Color"].default_value = (
    0.35,
    0.15,
    0.05,
    1.0,
)
node_rust_bsdf.inputs["Metallic"].default_value = 0.05
node_rust_bsdf.inputs["Roughness"].default_value = 0.85

# Mix Shader to blend Metal and Rust
node_mix_shader = nodes.new(type="ShaderNodeMixShader")
node_mix_shader.location = (550, 0)

# Noise Texture for the mask
node_noise = nodes.new(type="ShaderNodeTexNoise")
node_noise.location = (-300, 0)
node_noise.inputs["Scale"].default_value = 6.0
node_noise.inputs["Detail"].default_value = 12.0
node_noise.inputs["Roughness"].default_value = 0.6

# ColorRamp to control rust distribution (contrast and threshold)
node_ramp = nodes.new(type="ShaderNodeValToRGB")
node_ramp.location = (-50, 0)
# Adjust stops to make rust patches distinct
node_ramp.color_ramp.elements[0].position = 0.35
node_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)  # Metal
node_ramp.color_ramp.elements[1].position = 0.65
node_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)  # Rust

# Texture Coordinate & Mapping for realistic procedural placement
node_tex_coord = nodes.new(type="ShaderNodeTexCoord")
node_tex_coord.location = (-750, 0)

node_mapping = nodes.new(type="ShaderNodeMapping")
node_mapping.location = (-520, 0)

# --- Link Nodes ---

# Texture coordinate chain
links.new(node_tex_coord.outputs["Object"], node_mapping.inputs["Vector"])
links.new(node_mapping.outputs["Vector"], node_noise.inputs["Vector"])

# Noise to ColorRamp (Mask generation)
links.new(node_noise.outputs["Fac"], node_ramp.inputs["Fac"])

# Shaders to Mix Shader
links.new(node_metal_bsdf.outputs["BSDF"], node_mix_shader.inputs[1])
links.new(node_rust_bsdf.outputs["BSDF"], node_mix_shader.inputs[2])

# ColorRamp mask to Mix Shader Factor
links.new(node_ramp.outputs["Color"], node_mix_shader.inputs["Fac"])

# Mix Shader to Material Output
links.new(node_mix_shader.outputs["Shader"], node_output.inputs["Surface"])

# 4. Assign material to the cylinder
if cylinder.data.materials:
    cylinder.data.materials[0] = mat
else:
    cylinder.data.materials.append(mat)
