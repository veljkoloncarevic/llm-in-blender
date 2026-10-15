import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=64,
    radius=1,
    depth=2,
    enter_editmode=False,
    align='WORLD',
    location=(0, 0, 0),
    scale=(1, 1, 1)
)
cylinder = bpy.context.active_object

# Create a new material
mat = bpy.data.materials.new(name="Rusty_Metal")
mat.use_nodes = True
ntree = mat.node_tree
nodes = ntree.nodes
links = ntree.links

# Clear default nodes
nodes.clear()

# Node: Output
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)

# Node: Principled BSDF for grey metallic surface
metal_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
metal_bsdf.location = (-400, 100)
metal_bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1)
metal_bsdf.inputs['Metallic'].default_value = 1.0
metal_bsdf.inputs['Roughness'].default_value = 0.3

# Node: Principled BSDF for orange-brown rough rust
rust_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
rust_bsdf.location = (-400, -100)
rust_bsdf.inputs['Base Color'].default_value = (0.8, 0.3, 0.1, 1)
rust_bsdf.inputs['Metallic'].default_value = 0.0
rust_bsdf.inputs['Roughness'].default_value = 1.0

# Node: Noise texture as mask
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-600, 0)
noise.inputs['Scale'].default_value = 5.0
noise.inputs['Detail'].default_value = 4.0
noise.inputs['Roughness'].default_value = 0.5

# Node: Mix Shader
mix = nodes.new('ShaderNodeMixShader')
mix.location = (100, 0)

# Make connections
links.new(noise.outputs['Fac'], mix.inputs['Fac'])
links.new(metal_bsdf.outputs['BSDF'], mix.inputs[1])
links.new(rust_bsdf.outputs['BSDF'], mix.inputs[2])
links.new(mix.outputs['Shader'], output.inputs['Surface'])

# Assign material to the cylinder
if cylinder.data.materials:
    cylinder.data.materials.clear()
cylinder.data.materials.append(mat)
