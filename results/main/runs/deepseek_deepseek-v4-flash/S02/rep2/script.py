import bpy
import mathutils

# Switch to object mode to avoid edit mode issues
if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode='OBJECT')

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create floor plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Create red glossy cube, sitting on the floor
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.001))
cube = bpy.context.active_object
cube.name = "RedGlossyCube"

# --- Floor material: black and white checker ---
mat_floor = bpy.data.materials.new(name="FloorChecker")
mat_floor.use_nodes = True
nt_floor = mat_floor.node_tree
nt_floor.nodes.clear()

principled_floor = nt_floor.nodes.new(type='ShaderNodeBsdfPrincipled')
checker = nt_floor.nodes.new(type='ShaderNodeTexChecker')
out_floor = nt_floor.nodes.new(type='ShaderNodeOutputMaterial')

checker.inputs['Color1'].default_value = (0, 0, 0, 1)
checker.inputs['Color2'].default_value = (1, 1, 1, 1)
checker.inputs['Scale'].default_value = 2.0

# Position nodes for readability
principled_floor.location = (0, 0)
checker.location = (-300, 0)
out_floor.location = (200, 0)

nt_floor.links.new(checker.outputs['Color'], principled_floor.inputs['Base Color'])
nt_floor.links.new(principled_floor.outputs['BSDF'], out_floor.inputs['Surface'])

floor.data.materials.append(mat_floor)

# --- Cube material: glossy red ---
mat_cube = bpy.data.materials.new(name="RedGlossy")
mat_cube.use_nodes = True
nt_cube = mat_cube.node_tree
nt_cube.nodes.clear()

glossy = nt_cube.nodes.new(type='ShaderNodeBsdfGlossy')
out_cube = nt_cube.nodes.new(type='ShaderNodeOutputMaterial')

glossy.inputs['Color'].default_value = (1, 0, 0, 1)
glossy.inputs['Roughness'].default_value = 0.1

glossy.location = (0, 0)
out_cube.location = (200, 0)

nt_cube.links.new(glossy.outputs['BSDF'], out_cube.inputs['Surface'])

cube.data.materials.append(mat_cube)
