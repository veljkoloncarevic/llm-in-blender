# Hand-written reference solution (used by --smoke). Procedural wood, Blender 4.x API.
import bpy

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=1)
plank = bpy.context.active_object
plank.name = "Plank"
plank.scale = (2.0, 0.4, 0.08)

mat = bpy.data.materials.new("Wood")
mat.use_nodes = True
nt = mat.node_tree
n, l = nt.nodes, nt.links
bsdf = n["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.6

coord = n.new("ShaderNodeTexCoord")
mapping = n.new("ShaderNodeMapping")
mapping.inputs["Scale"].default_value = (1.0, 6.0, 6.0)
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 3.0
noise.inputs["Detail"].default_value = 6.0
wave = n.new("ShaderNodeTexWave")
wave.wave_type = "RINGS"
wave.inputs["Scale"].default_value = 2.0
wave.inputs["Distortion"].default_value = 6.0
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.18, 0.08, 0.03, 1.0)
ramp.color_ramp.elements[1].color = (0.55, 0.32, 0.15, 1.0)
bump = n.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.3

l.new(coord.outputs["Object"], mapping.inputs["Vector"])
l.new(mapping.outputs["Vector"], noise.inputs["Vector"])
l.new(noise.outputs["Color"], wave.inputs["Vector"])
l.new(wave.outputs["Fac"], ramp.inputs["Fac"])
l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
l.new(wave.outputs["Fac"], bump.inputs["Height"])
l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

plank.data.materials.append(mat)
