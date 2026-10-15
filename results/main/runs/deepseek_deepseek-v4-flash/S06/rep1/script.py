import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a wooden plank as a scaled cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
plank = bpy.context.active_object
plank.name = "WoodPlank"
plank.scale = (2.0, 0.2, 0.1)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Create procedural wood material
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

# Create nodes
texcoord = nt.nodes.new(type='ShaderNodeTexCoord')
mapping = nt.nodes.new(type='ShaderNodeMapping')
noise = nt.nodes.new(type='ShaderNodeTexNoise')
wave = nt.nodes.new(type='ShaderNodeTexWave')
ramp = nt.nodes.new(type='ShaderNodeValToRGB')
bump = nt.nodes.new(type='ShaderNodeBump')
bsdf = nt.nodes.new(type='ShaderNodeBsdfPrincipled')
output = nt.nodes.new(type='ShaderNodeOutputMaterial')

# Node layout
texcoord.location = (-900, 100)
mapping.location = (-700, 100)
noise.location = (-700, -150)
wave.location = (-500, 100)
ramp.location = (-250, 200)
bump.location = (-250, -100)
bsdf.location = (0, 100)
output.location = (250, 100)

# Configure wave and noise
wave.wave_type = 'BANDS'
wave.bands_direction = 'X'
wave.inputs['Scale'].default_value = 4.0
wave.inputs['Distortion'].default_value = 2.0
wave.inputs['Detail'].default_value = 4.0
wave.inputs['Detail Scale'].default_value = 2.0

noise.inputs['Scale'].default_value = 3.0
noise.inputs['Detail'].default_value = 2.0
noise.inputs['Roughness'].default_value = 0.5

# Configure color ramp with brown tones
ramp.color_ramp.interpolation = 'LINEAR'
elements = ramp.color_ramp.elements
elements[0].position = 0.0
elements[0].color = (0.08, 0.04, 0.02, 1.0)
mid = elements.new(0.45)
mid.color = (0.35, 0.20, 0.10, 1.0)
elements[1].position = 1.0
elements[1].color = (0.65, 0.45, 0.25, 1.0)

# Configure bump
bump.inputs['Strength'].default_value = 0.4
bump.inputs['Distance'].default_value = 0.02

# Node links
nt.links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
nt.links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
nt.links.new(noise.outputs['Fac'], wave.inputs['Distortion'])
nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
nt.links.new(wave.outputs['Fac'], bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
nt.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to plank
if plank.data.materials:
    plank.data.materials[0] = mat
else:
    plank.data.materials.append(mat)
