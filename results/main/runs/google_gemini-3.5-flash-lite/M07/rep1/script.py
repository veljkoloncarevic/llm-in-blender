import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create a 4x4 base plane
bpy.ops.mesh.primitive_plane_size(size=4.0, enter_editmode=False, align='WORLD', location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "PebbleScatterPlane"

# 2. Create the source pebble (Icosphere with sufficient resolution for high face count)
# Using subdivisions = 3 gives 1,280 faces per icosphere. 
# 200 pebbles * 1280 = 256,000 faces (or slightly less via random scaling, safely in range).
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, subdivisions=3, location=(0, 0, -10))
pebble = bpy.context.active_object
pebble.name = "SourcePebble"

# 3. Add Geometry Nodes modifier to the plane
modifier = plane.modifiers.new(name="PebbleScatter", TYPE='NODES')
node_group = bpy.data.node_groups.new(name="PebbleScatterGeometry", type='GeometryNodeTree')
modifier.node_group = node_group

# Setup node tree interface inputs/outputs
node_group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
node_group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

nodes = node_group.nodes
links = node_group.links

# Create nodes
group_input = nodes.new('NodeGroupInput')
group_input.location = (-600, 0)

group_output = nodes.new('NodeGroupOutput')
group_output.location = (600, 0)

# Distribute Points on Faces
distribute_node = nodes.new('GeometryNodeDistributePointsOnFaces')
distribute_node.location = (-400, 0)
# Set density/count roughly to 200 points
distribute_node.inputs['Density'].default_value = 12.5 # ~12.5 points per sq meter on a 4x4 (16m²) plane = ~200 points
distribute_node.inputs['Seed'].default_value = 42

# Instance on Points
instance_node = nodes.new('GeometryNodeInstanceOnPoints')
instance_node.location = (-150, 0)

# Object Info (to reference our pebble)
obj_info_node = nodes.new('GeometryNodeObjectInfo')
obj_info_node.location = (-400, -200)
obj_info_node.inputs['Object'].default_value = pebble

# Random Value for Scale
scale_random = nodes.new('FunctionNodeRandomValue')
scale_random.location = (-400, 200)
scale_random.data_type = 'FLOAT_VECTOR'
scale_random.inputs['Min'].default_value = (0.05, 0.05, 0.05)
scale_random.inputs['Max'].default_value = (0.15, 0.15, 0.15)

# Random Value for Rotation
rot_random = nodes.new('FunctionNodeRandomValue')
rot_random.location = (-400, 380)
rot_random.data_type = 'FLOAT_VECTOR'
# Max rotation in radians (0 to 2*pi)
rot_random.inputs['Min'].default_value = (0.0, 0.0, 0.0)
rot_random.inputs['Max'].default_value = (6.28318, 6.28318, 6.28318)

# Connect nodes
links.new(group_input.outputs['Geometry'], distribute_node.inputs['Mesh'])
links.new(distribute_node.outputs['Points'], instance_node.inputs['Points'])
links.new(obj_info_node.outputs['Geometry'], instance_node.inputs['Instance'])
links.new(scale_random.outputs['Value'], instance_node.inputs['Scale'])
links.new(rot_random.outputs['Value'], instance_node.inputs['Rotation'])
links.new(instance_node.outputs['Instances'], group_output.inputs['Geometry'])

# Optional: Hide the source pebble from viewport/render
pebble.hide_viewport = True
pebble.hide_render = True
