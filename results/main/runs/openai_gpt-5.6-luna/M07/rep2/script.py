import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (
    bpy.data.meshes,
    bpy.data.curves,
    bpy.data.materials,
    bpy.data.cameras,
    bpy.data.lights,
):
    pass

# Create a 4 x 4 plane
plane_mesh = bpy.data.meshes.new("ScatterPlaneMesh")
plane_mesh.from_pydata(
    [(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)],
    [],
    [(0, 1, 2, 3)]
)
plane_mesh.update()

plane_obj = bpy.data.objects.new("PebbleScatterPlane", plane_mesh)
bpy.context.collection.objects.link(plane_obj)

# Create a high-detail icosphere pebble source
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.0,
    location=(0, 0, -100)
)
pebble_obj = bpy.context.object
pebble_obj.name = "PebbleSource"
pebble_obj.hide_set(True)
pebble_obj.hide_render = True

# Slightly flatten and irregularize the pebble source
pebble_obj.scale = (1.0, 0.9, 0.55)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Create Geometry Nodes node group
node_group = bpy.data.node_groups.new("PebbleScatterGeometry", "GeometryNodeTree")

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

group_input = nodes.new("NodeGroupInput")
group_input.name = "Plane Input"
group_input.label = "4 x 4 Scatter Plane"
group_input.location = (-650, 0)

group_output = nodes.new("NodeGroupOutput")
group_output.name = "Scattered Pebbles Output"
group_output.location = (500, 0)

distribute = nodes.new("GeometryNodeDistributePointsOnFaces")
distribute.name = "Distribute About 200 Points"
distribute.label = "About 200 Pebbles"
distribute.distribute_method = 'RANDOM'
distribute.location = (-400, 0)
distribute.inputs["Density"].default_value = 12.5
distribute.inputs["Seed"].default_value = 37

object_info = nodes.new("GeometryNodeObjectInfo")
object_info.name = "Pebble Source Object"
object_info.label = "Icosphere Pebble"
object_info.location = (-400, -240)
object_info.transform_space = 'ORIGINAL'
object_info.inputs["Object"].default_value = pebble_obj
object_info.inputs["As Instance"].default_value = True

random_scale = nodes.new("FunctionNodeRandomValue")
random_scale.name = "Random Pebble Size"
random_scale.label = "Random Size"
random_scale.data_type = 'FLOAT'
random_scale.location = (-150, -100)
random_scale.inputs["Min"].default_value = 0.045
random_scale.inputs["Max"].default_value = 0.13
random_scale.inputs["Seed"].default_value = 101

combine_scale = nodes.new("ShaderNodeCombineXYZ")
combine_scale.name = "Uniform Pebble Scale"
combine_scale.location = (20, -100)

random_rotation = nodes.new("FunctionNodeRandomValue")
random_rotation.name = "Random Pebble Rotation"
random_rotation.label = "Random Rotation"
random_rotation.data_type = 'FLOAT_VECTOR'
random_rotation.location = (-150, -300)
random_rotation.inputs["Min"].default_value = (0.0, 0.0, 0.0)
random_rotation.inputs["Max"].default_value = (
    2.0 * math.pi,
    2.0 * math.pi,
    2.0 * math.pi,
)
random_rotation.inputs["Seed"].default_value = 202

instance_on_points = nodes.new("GeometryNodeInstanceOnPoints")
instance_on_points.name = "Instance Icosphere Pebbles"
instance_on_points.label = "Instance on Points"
instance_on_points.location = (250, 0)

links.new(group_input.outputs["Geometry"], distribute.inputs["Mesh"])
links.new(distribute.outputs["Points"], instance_on_points.inputs["Points"])
links.new(object_info.outputs["Geometry"], instance_on_points.inputs["Instance"])
links.new(random_scale.outputs["Value"], combine_scale.inputs["X"])
links.new(random_scale.outputs["Value"], combine_scale.inputs["Y"])
links.new(random_scale.outputs["Value"], combine_scale.inputs["Z"])
links.new(combine_scale.outputs["Vector"], instance_on_points.inputs["Scale"])
links.new(random_rotation.outputs["Value"], instance_on_points.inputs["Rotation"])
links.new(instance_on_points.outputs["Instances"], group_output.inputs["Geometry"])

# Add the Geometry Nodes modifier to the plane
modifier = plane_obj.modifiers.new(
    name="Pebble Scatter Geometry Nodes",
    type='NODES'
)
modifier.node_group = node_group

# Keep the plane selected and active
bpy.context.view_layer.objects.active = plane_obj
plane_obj.select_set(True)
