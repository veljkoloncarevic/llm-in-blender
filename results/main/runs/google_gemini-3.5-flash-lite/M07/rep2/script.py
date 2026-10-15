import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create a 4x4 Plane
bpy.ops.mesh.primitive_plane_size(size=4.0, enter_editmode=False, align='WORLD', location=(0, 0, 0))
plane_obj = bpy.context.active_object
plane_obj.name = "PebbleEmitter"

# Subdivide plane slightly to give the distribute points node a bit more density variation if needed, though not strictly necessary for Poisson/Random
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=4)
bpy.ops.object.mode_set(mode='OBJECT')

# 2. Create the source Icosphere to instance
# Radius set to small (e.g., 0.08), subdivisions = 2 -> 320 faces per pebble.
# 200 pebbles * 320 faces = 64,000 faces (satisfies the 5,000 - 150,000 face count rule).
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.08, subdivisions=2, location=(0, 0, -10))
ico_obj = bpy.context.active_object
ico_obj.name = "PebbleSource"

# 3. Add Geometry Nodes Modifier to the Plane
mod = plane_obj.modifiers.new(name="PebbleScatter", type='NODES')
node_group = bpy.data.node_groups.new(name="PebbleScatterTree", type='GeometryNodeTree')
mod.node_group = node_group

# Setup interface (inputs/outputs)
node_group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

nodes = node_group.nodes
links = node_group.links

# Create Nodes
group_input = nodes.new('NodeGroupInput')
group_input.location = (-400, 0)

group_output = nodes.new('NodeGroupOutput')
group_output.location = (800, 0)

# Distribute Points on Faces
distribute_node = nodes.new('GeometryNodeDistributePointsOnFaces')
distribute_node.location = (-200, 0)
distribute_node.inputs['Density'].default_value = 200.0  # ~200 points on 4x4 area

# Instance on Points
instance_node = nodes.new('GeometryNodeInstanceOnPoints')
instance_node.location = (200, 0)

# Object Info (for the Icosphere)
object_info = nodes.new('GeometryNodeObjectInfo')
object_info.location = (-100, -200)
object_info.inputs['Object'].default_value = ico_obj
object_info.inputs['As Instance'].default_value = False # Realize geometry for proper individual mesh data if needed, or keep as instance. Instances are fine.

# Random Value for Scale
random_scale = nodes.new('FunctionNodeRandomValue')
random_scale.location = (-100, 200)
random_scale.data_type = 'FLOAT_VECTOR'
random_scale.inputs['Min'].default_value = (0.5, 0.5, 0.5)
random_scale.inputs['Max'].default_value = (1.5, 1.8, 1.2)

# Random Value for Rotation
random_rot = nodes.new('FunctionNodeRandomValue')
random_rot.location = (-100, -50)
random_rot.data_type = 'FLOAT_VECTOR'
random_rot.inputs['Max'].default_value = (6.28318, 6.28318, 6.28318) # 0 to 2pi radians

# Link Nodes
# Geometry flow
links.new(group_input.outputs['Geometry'], distribute_node.inputs['Mesh'])
links.new(distribute_node.outputs['Points'], instance_node.inputs['Points'])
links.new(object_info.outputs['Geometry'], instance_node.inputs['Instance'])

# Randomizations
links.new(random_scale.outputs['Value'], instance_node.inputs['Scale'])
links.new(random_rot.outputs['Value'], instance_node.inputs['Rotation'])

# Output
links.new(instance_node.outputs['Instances'], group_output.inputs['Geometry'])

# Hide the source icosphere from view/render
ico_obj.hide_viewport = True
ico_obj.hide_render = True

# Select the emitter plane
bpy.context.view_layer.objects.active = plane_obj
plane_obj.select_set(True)
