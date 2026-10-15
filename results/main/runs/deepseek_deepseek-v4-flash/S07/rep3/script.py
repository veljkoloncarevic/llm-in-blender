import bpy
import mathutils

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.0,
    vertices=32,
    location=(0.0, 0.0, 0.0)
)
obj = bpy.context.active_object
obj.name = "RustyCylinder"

# Create rusty metal material
mat = bpy.data.materials.new(name="RustyMetal")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

# ---- Create nodes ----
# Output
out = nt.nodes.new('ShaderNodeOutputMaterial')
out.location = (300, 0)

# Mix Shader
mix = nt.nodes.new('ShaderNodeMixShader')
mix.location = (100, 0)
mix.inputs[0].default_value = 0.5

# Metal Principled BSDF
metal = nt.nodes.new('ShaderNodeBsdfPrincipled')
metal.location = (-200, 200)
metal.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
metal.inputs['Metallic'].default_value = 1.0
metal.inputs['Roughness'].default_value = 0.3

# Rust Principled BSDF
rust = nt.nodes.new('ShaderNodeBsdfPrincipled')
rust.location = (-200, -100)
rust.inputs['Base Color'].default_value = (0.6, 0.25, 0.05, 1.0)
rust.inputs['Metallic'].default_value = 0.0
rust.inputs['Roughness'].default_value = 0.8

# Texture Coordinate
tex_coord = nt.nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-600, 0)

# Noise Texture
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 0)
noise.inputs['Scale'].default_value = 3.0

# ColorRamp to sharpen mask contrast
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.location = (-200, 0)
ramp.color_ramp.elements[0].position = 0.3
ramp.color_ramp.elements[1].position = 0.7

# ---- Connect nodes ----
nt.links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
nt.links.new(noise.outputs['Fac'], ramp.inputs[0])
nt.links.new(ramp.outputs['Color'], mix.inputs['Fac'])
nt.links.new(metal.outputs['BSDF'], mix.inputs[1])
nt.links.new(rust.outputs['BSDF'], mix.inputs[2])
nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])

# Assign material to cylinder
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
