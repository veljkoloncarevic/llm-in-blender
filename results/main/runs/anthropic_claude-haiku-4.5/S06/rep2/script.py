import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a cube mesh
mesh = bpy.data.meshes.new("PlaneMesh")
obj = bpy.data.objects.new("WoodenPlank", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Create cube geometry
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2)
bm.to_mesh(mesh)
bm.free()
mesh.update()

# Scale to plank proportions (long, narrow, thin)
obj.scale = (4, 0.5, 0.2)

# Create material
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create shader nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')

# Create texture nodes
wave_texture = nodes.new(type='ShaderNodeTexWave')
noise_texture = nodes.new(type='ShaderNodeTexNoise')
color_ramp = nodes.new(type='ShaderNodeValRamp')
bump_node = nodes.new(type='ShaderNodeBump')

# Configure Wave texture
wave_texture.inputs['Scale'].default_value = 5.0
wave_texture.inputs['Distortion'].default_value = 1.0

# Configure Noise texture for distortion
noise_texture.inputs['Scale'].default_value = 15.0
noise_texture.inputs['Detail'].default_value = 5.0

# Configure Color Ramp for brown wood tones
color_ramp.color_ramp.elements[0].color = (0.3, 0.15, 0.05, 1.0)  # Dark brown
color_ramp.color_ramp.elements[1].color = (0.7, 0.5, 0.25, 1.0)   # Light brown

# Configure Bump node
bump_node.inputs['Strength'].default_value = 0.8
bump_node.inputs['Distance'].default_value = 1.0

# Connect nodes for the texture pipeline
# Wave texture distorted by Noise
links.new(noise_texture.outputs['Fac'], wave_texture.inputs['Distortion'])

# Wave output to Color Ramp
links.new(wave_texture.outputs['Fac'], color_ramp.inputs['Fac'])

# Color Ramp to Base Color
links.new(color_ramp.outputs['Color'], bsdf_node.inputs['Base Color'])

# Same pattern to Bump node
links.new(wave_texture.outputs['Fac'], bump_node.inputs['Height'])

# Bump to Normal
links.new(bump_node.outputs['Normal'], bsdf_node.inputs['Normal'])

# Connect BSDF to output
links.new(bsdf_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to object
obj.data.materials.append(mat)

# Set viewport shading to Material Preview or Rendered for visibility
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
