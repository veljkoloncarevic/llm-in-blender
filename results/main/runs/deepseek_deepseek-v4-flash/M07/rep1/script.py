import bpy

# Clear existing objects
if bpy.context.object:
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4x4 plane
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "Plane"

# Create a Geometry Nodes group
gn = bpy.data.node_groups.new(name="PebbleScatter", type="GeometryNodeTree")
gn.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
gn.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

nodes = gn.nodes
links = gn.links

# Add nodes
group_in = nodes.new("NodeGroupInput")
group_out = nodes.new("NodeGroupOutput")
distribute = nodes.new("GeometryNodeDistributePointsOnFaces")
instance_on_points = nodes.new("GeometryNodeInstanceOnPoints")
ico = nodes.new("GeometryNodeMeshIcoSphere")
rand_scale = nodes.new("FunctionNodeRandomValue")
rand_rot = nodes.new("FunctionNodeRandomValue")
realize = nodes.new("GeometryNodeRealizeInstances")
join_geom = nodes.new("GeometryNodeJoinGeometry")

# Arrange nodes
group_in.location = (-800, 0)
distribute.location = (-600, 0)
instance_on_points.location = (-300, 0)
realize.location = (0, 0)
join_geom.location = (200, 0)
group_out.location = (400, 0)
ico.location = (-600, -300)
rand_scale.location = (-600, -200)
rand_rot.location = (-600, -400)

# Set node properties
try:
    distribute.method = 'RANDOM'
except AttributeError:
    distribute.distribute_method = 'RANDOM'

distribute.inputs["Count"].default_value = 200
distribute.inputs["Seed"].default_value = 5

ico.inputs["Radius"].default_value = 0.1
ico.inputs["Subdivisions"].default_value = 2

rand_scale.data_type = 'FLOAT'
rand_scale.inputs["Min"].default_value = 0.5
rand_scale.inputs["Max"].default_value = 1.5
rand_scale.inputs["Seed"].default_value = 10

rand_rot.data_type = 'FLOAT_VECTOR'
rand_rot.inputs["Min"].default_value = (0.0, 0.0, 0.0)
rand_rot.inputs["Max"].default_value = (6.283, 6.283, 6.283)
rand_rot.inputs["Seed"].default_value = 20

# Connect nodes
links.new(group_in.outputs["Geometry"], distribute.inputs["Mesh"])
links.new(distribute.outputs["Points"], instance_on_points.inputs["Points"])
links.new(ico.outputs["Mesh"], instance_on_points.inputs["Instance"])
links.new(rand_scale.outputs["Value"], instance_on_points.inputs["Scale"])
links.new(rand_rot.outputs["Value"], instance_on_points.inputs["Rotation"])
links.new(instance_on_points.outputs["Instances"], realize.inputs["Geometry"])
links.new(realize.outputs["Geometry"], join_geom.inputs[0])
links.new(group_in.outputs["Geometry"], join_geom.inputs[1])
links.new(join_geom.outputs["Geometry"], group_out.inputs["Geometry"])

# Add Geometry Nodes modifier to the plane
mod = plane.modifiers.new("PebbleScatter", "NODES")
mod.node_group = gn
