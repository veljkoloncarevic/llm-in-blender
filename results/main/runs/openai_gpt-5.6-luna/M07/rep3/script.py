import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the 4 x 4 base plane
bpy.ops.mesh.primitive_plane_add(size=4.0, location=(0.0, 0.0, 0.0))
plane = bpy.context.object
plane.name = "Pebble Scatter Plane"

# Create the pebble source mesh
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.0,
    location=(0.0, 0.0, -100.0)
)
pebble = bpy.context.object
pebble.name = "Pebble Source"
pebble.hide_render = True
pebble.hide_set(True)

# Create the Geometry Nodes modifier and node group
modifier = plane.modifiers.new(name="Pebble Scattering", type='NODES')
node_group = bpy.data.node_groups.new("Pebble Scattering Geometry", "GeometryNodeTree")
modifier.node_group = node_group

# Geometry Nodes interface
node_group.interface.new_socket(
    name="Geometry",
    in_out='INPUT',
    socket_type='NodeSocketGeometry'
)
node_group.interface.new_socket(
    name="Geometry",
    in_out='OUTPUT',
    socket_type='NodeSocketGeometry'
)

nodes = node_group.nodes
links = node_group.links
nodes.clear()

group_input = nodes.new("NodeGroupInput")
group_input.location = (-600, 0)

group_output = nodes.new("NodeGroupOutput")
group_output.location = (500, 0)

distribute = nodes.new("GeometryNodeDistributePointsOnFaces")
distribute.location = (-350, 0)
distribute.distribute_method = 'RANDOM'
distribute.inputs["Density"].default_value = 12.5
distribute.inputs["Seed"].default_value = 42

object_info = nodes.new("GeometryNodeObjectInfo")
object_info.location = (-350, -220)
object_info.transform_space = 'ORIGINAL'
object_info.inputs["Object"].default_value = pebble
object_info.inputs["As Instance"].default_value = False

random_scale = nodes.new("FunctionNodeRandomValue")
random_scale.location = (-100, -120)
random_scale.data_type = 'FLOAT'
random_scale.inputs["Min"].default_value = 0.035
random_scale.inputs["Max"].default_value = 0.095
random_scale.inputs["Seed"].default_value = 17

random_rotation = nodes.new("FunctionNodeRandomValue")
random_rotation.location = (-100, -300)
random_rotation.data_type = 'FLOAT_VECTOR'
random_rotation.inputs["Min"].default_value = Vector((0.0, 0.0, 0.0))
random_rotation.inputs["Max"].default_value = Vector((
    2.0 * math.pi,
    2.0 * math.pi,
    2.0 * math.pi
))
random_rotation.inputs["Seed"].default_value = 31

instance = nodes.new("GeometryNodeInstanceOnPoints")
instance.location = (150, 0)

links.new(group_input.outputs["Geometry"], distribute.inputs["Mesh"])
links.new(distribute.outputs["Points"], instance.inputs["Points"])
links.new(object_info.outputs["Geometry"], instance.inputs["Instance"])
links.new(random_scale.outputs["Value"], instance.inputs["Scale"])
links.new(random_rotation.outputs["Value"], instance.inputs["Rotation"])
links.new(instance.outputs["Instances"], group_output.inputs["Geometry"])

# Keep the plane selected and active
bpy.context.view_layer.objects.active = plane
plane.select_set(True)
