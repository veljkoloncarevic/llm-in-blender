import bpy
import bmesh
import mathutils

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4x4 plane
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.object
plane.name = "PebblePlane"

# Add Geometry Nodes modifier
mod = plane.modifiers.new(name="PebblesGN", type='NODES')

# Create node group
node_group = bpy.data.node_groups.new(name="Pebbles", type='GeometryNodeTree')
mod.node_group = node_group

# Add interface sockets
iface = node_group.interface
iface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
iface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Add nodes
nodes = node_group.nodes
links = node_group.links

group_in = nodes.new('NodeGroupInput')
group_out = nodes.new('NodeGroupOutput')
distribute = nodes.new('GeometryNodeDistributePointsOnFaces')
instance = nodes.new('GeometryNodeInstanceOnPoints')
icosphere = nodes.new('GeometryNodeIcoSphere')
scale_random = nodes.new('FunctionNodeRandomValue')
rot_random = nodes.new('FunctionNodeRandomValue')
combine = nodes.new('FunctionNodeCombineXYZ')

# Configure nodes
distribute.inputs["Density"].default_value = 12.5  # ~200 points on 4x4 plane
icosphere.inputs["Radius"].default_value = 0.2
icosphere.inputs["Subdivisions"].default_value = 2

scale_random.data_type = 'FLOAT'
scale_random.inputs["Min"].default_value = 0.1
scale_random.inputs["Max"].default_value = 0.3

rot_random.data_type = 'VECTOR'
rot_random.inputs["Min"].default_value = (-3.14159, -3.14159, -3.14159)
rot_random.inputs["Max"].default_value = (3.14159, 3.14159, 3.14159)

# Connect nodes
links.new(group_in.outputs["Geometry"], distribute.inputs["Mesh"])
links.new(distribute.outputs["Points"], instance.inputs["Points"])
links.new(icosphere.outputs["Mesh"], instance.inputs["Instance"])
links.new(scale_random.outputs["Value"], combine.inputs["X"])
links.new(scale_random.outputs["Value"], combine.inputs["Y"])
links.new(scale_random.outputs["Value"], combine.inputs["Z"])
links.new(combine.outputs["Vector"], instance.inputs["Scale"])
links.new(rot_random.outputs["Value"], instance.inputs["Rotation"])
links.new(instance.outputs["Instances"], group_out.inputs["Geometry"])

# Arrange nodes for readability (optional)
group_in.location = (-800, 0)
distribute.location = (-500, 0)
icosphere.location = (-500, -200)
scale_random.location = (-500, 200)
rot_random.location = (-500, 100)
combine.location = (-300, 200)
instance.location = (-100, 0)
group_out.location = (200, 0)
