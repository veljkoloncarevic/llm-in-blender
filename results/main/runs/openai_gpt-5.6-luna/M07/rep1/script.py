import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4 x 4 plane mesh
plane_mesh = bpy.data.meshes.new("ScatterPlaneMesh")
bm = bmesh.new()
bmesh.ops.create_grid(
    bm,
    x_segments=1,
    y_segments=1,
    size=2.0
)
bm.to_mesh(plane_mesh)
bm.free()

plane_obj = bpy.data.objects.new("Pebble Scatter Plane", plane_mesh)
bpy.context.collection.objects.link(plane_obj)

# Scale the default 2 x 2 grid to 4 x 4
plane_obj.scale = (2.0, 2.0, 1.0)
bpy.context.view_layer.objects.active = plane_obj
plane_obj.select_set(True)

# Create a low-poly icosphere pebble source
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.0,
    location=(0.0, 0.0, -10.0)
)
pebble_obj = bpy.context.active_object
pebble_obj.name = "Pebble Instance Source"
pebble_obj.hide_render = True
pebble_obj.hide_set(True)
pebble_obj.select_set(False)

# Geometry Nodes modifier
modifier = plane_obj.modifiers.new(
    name="Pebble Geometry Nodes",
    type='NODES'
)

node_group = bpy.data.node_groups.new(
    "Scatter About 200 Pebbles",
    "GeometryNodeTree"
)
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
group_input.name = "Plane Input"
group_input.label = "4 x 4 Plane"
group_input.location = (-650, 80)

group_output = nodes.new("NodeGroupOutput")
group_output.name = "Pebble Output"
group_output.location = (420, 80)

distribute = nodes.new("GeometryNodeDistributePointsOnFaces")
distribute.name = "Distribute About 200 Points"
distribute.label = "About 200 Pebbles"
distribute.distribute_method = 'RANDOM'
distribute.location = (-400, 80)
distribute.inputs["Density"].default_value = 12.5
distribute.inputs["Seed"].default_value = 37

object_info = nodes.new("GeometryNodeObjectInfo")
object_info.name = "Pebble Source"
object_info.label = "Icosphere Pebble"
object_info.location = (-380, -180)
object_info.transform_space = 'ORIGINAL'
object_info.inputs["Object"].default_value = pebble_obj
object_info.inputs["As Instance"].default_value = True

random_scale = nodes.new("FunctionNodeRandomValue")
random_scale.name = "Random Pebble Size"
random_scale.label = "Random Size"
random_scale.data_type = 'FLOAT'
random_scale.location = (-120, -40)
random_scale.inputs["Min"].default_value = 0.055
random_scale.inputs["Max"].default_value = 0.145
random_scale.inputs["ID"].default_value = 11

random_rotation = nodes.new("FunctionNodeRandomValue")
random_rotation.name = "Random Pebble Rotation"
random_rotation.label = "Random Rotation"
random_rotation.data_type = 'ROTATION'
random_rotation.location = (-120, -180)
random_rotation.inputs["Min"].default_value = (-3.14159, -3.14159, -3.14159)
random_rotation.inputs["Max"].default_value = (3.14159, 3.14159, 3.14159)
random_rotation.inputs["ID"].default_value = 23

instance = nodes.new("GeometryNodeInstanceOnPoints")
instance.name = "Instance Pebbles"
instance.label = "Instance Icospheres"
instance.location = (150, 80)

links.new(
    group_input.outputs["Geometry"],
    distribute.inputs["Mesh"]
)
links.new(
    distribute.outputs["Points"],
    instance.inputs["Points"]
)
links.new(
    object_info.outputs["Geometry"],
    instance.inputs["Instance"]
)
links.new(
    random_scale.outputs["Value"],
    instance.inputs["Scale"]
)
links.new(
    random_rotation.outputs["Value"],
    instance.inputs["Rotation"]
)
links.new(
    instance.outputs["Instances"],
    group_output.inputs["Geometry"]
)

# Keep the scatter plane selected and active
bpy.context.view_layer.objects.active = plane_obj
plane_obj.select_set(True)
