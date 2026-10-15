import bpy

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0, depth=3.0, location=(0, 0, 0)
)
cylinder = bpy.active_object
cylinder.name = "RustyCylinder"

# Ensure smooth shading for better appearance
for polygon in cylinder.data.polygons:
    polygon.use_smooth = True

# 3. Create a procedural rusty metal material using nodes
mat = bpy.data.materials.new(name="RustyMetalMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes to build our specific network
nodes.clear()

# --- Create Nodes ---

# Output
node_output = nodes.new(type="ShaderNodeOutputMaterial")
node_output.location = (600, 0)

# Mix Shader to blend clean metal and rust
node_mix_shader = nodes.new(type="ShaderNodeMixShader")
node_mix_shader.location = (380, 0)

# Clean Metal Shader (Principled BSDF)
node_metal = nodes.new(type="ShaderNodeBsdfPrincipled")
node_metal.location = (100, 150)
node_metal.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)  # Grey
node_metal.inputs["Metallic"].default_value = 0.95
node_metal.inputs["Roughness"].default_value = 0.2

# Rust Shader (Principled BSDF)
node_rust = nodes.new(type="ShaderNodeBsdfPrincipled")
node_rust.location = (100, -150)
node_rust.inputs["Base Color"].default_value = (
    0.28,
    0.11,
    0.03,
    1.0,
)  # Orange-brown
node_rust.inputs["Metallic"].default_value = 0.05
node_rust.inputs["Roughness"].default_value = 0.85

# Texture Coordinate & Mapping for procedural placement
node_tex_coord = nodes.new(type="ShaderNodeTexCoord")
node_tex_coord.location = (-640, 0)

node_mapping = nodes.new(type="ShaderNodeMapping")
node_mapping.location = (-460, 0)

# Noise Texture to drive the rust mask
node_noise = nodes.new(type="ShaderNodeTexNoise")
node_noise.location = (-280, 0)
node_noise.inputs["Scale"].default_value = 8.0
node_noise.inputs["Detail"].default_value = 12.0
node_noise.inputs["Roughness"].default_value = 0.65

# Color Ramp to control the distribution and sharpness of the rust
node_color_ramp = nodes.new(type="ShaderNodeValToRGB")
node_color_ramp.location = (-60, 0)
# Adjust stops to make rust patches balanced
node_color_ramp.color_ramp.elements[0].position = 0.38
node_color_ramp.color_ramp.elements[1].position = 0.62

# --- Link Nodes ---

# Texture coordinate flow
links.new(node_tex_coord.outputs["Object"], node_mapping.inputs["Vector"])
links.new(node_mapping.outputs["Vector"], node_noise.inputs["Vector"])

# Noise drives Color Ramp, which acts as the Mix factor
links.new(node_noise.outputs["Fac"], node_color_ramp.inputs["Fac"])
links.new(node_color_ramp.outputs["Color"], node_mix_shader.inputs["Fac"])

# Shaders into Mix Shader
links.new(node_metal.outputs["BSDF"], node_mix_shader.inputs[1])
links.new(node_rust.outputs["BSDF"], node_mix_shader.inputs[2])

# Mix Shader to Material Output
links.new(node_mix_shader.outputs["Shader"], node_output.inputs["Surface"])

# 4. Assign the material to the cylinder
if cylinder.data.materials:
    cylinder.data.materials[0] = mat
else:
    cylinder.data.materials.append(mat)
