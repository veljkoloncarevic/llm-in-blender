import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cylinder
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1, depth=2, location=(0, 0, 0))
obj = bpy.context.active_object
obj.name = "RustyCylinder"
bpy.ops.object.shade_smooth()

# Create material
mat = bpy.data.materials.new(name="RustyMetal")
mat.use_nodes = True
nt = mat.node_tree
nodes = nt.nodes
links = nt.links

# Clear default nodes
nodes.clear()

# Create node group
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)

mix = nodes.new('ShaderNodeMixShader')
mix.location = (200, 0)

noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 0)
noise.inputs['Scale'].default_value = 2.0
noise.inputs['Detail'].default_value = 2.0
noise.inputs['Distortion'].default_value = 0.0

metal = nodes.new('ShaderNodeBsdfPrincipled')
metal.location = (0, 200)
metal.inputs['Base Color'].default_value = (0.5, 0.5, 0.5, 1.0)
metal.inputs['Metallic'].default_value = 1.0
metal.inputs['Roughness'].default_value = 0.3

rust = nodes.new('ShaderNodeBsdfPrincipled')
rust.location = (0, -200)
rust.inputs['Base Color'].default_value = (0.6, 0.3, 0.1, 1.0)  # orange-brown
rust.inputs['Metallic'].default_value = 0.0
rust.inputs['Roughness'].default_value = 1.0

# Connect nodes
links.new(noise.outputs['Fac'], mix.inputs['Fac'])
links.new(metal.outputs['BSDF'], mix.inputs[1])
links.new(rust.outputs['BSDF'], mix.inputs[2])
links.new(mix.outputs['BSDF'], output.inputs['Surface'])

# Assign material to the cylinder
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
