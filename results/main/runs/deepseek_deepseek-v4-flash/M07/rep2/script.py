import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4x4 plane (centered at origin)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.object
plane.name = "Pebble_Plane"

# Add a Geometry Nodes modifier
modifier = plane.modifiers.new("PebbleScatter", 'NODES')
group = bpy.data.node_groups.new("PebbleScatter", type='GeometryNodeTree')
modifier.node_group = group

# Add a geometry input/output socket to the group interface
group.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Build the node tree
nodes = group.nodes
links = group.links

group_input = nodes.new("NodeGroupInput")
group_output = nodes.new("NodeGroupOutput")
distribute = nodes.new("GeometryNodeDistributePointsOnFaces")
ico_sphere = nodes.new("GeometryNodeMeshIcoSphere")
instance = nodes.new("GeometryNodeInstanceOnPoints")
scale_inst = nodes.new("GeometryNodeScaleInstances")
realize = nodes.new("GeometryNodeRealizeInstances")
random_scale = nodes.new("FunctionNodeRandomValue")
random_rot = nodes.new("FunctionNodeRandomValue")
add_rot = nodes.new("ShaderNodeVectorMath")

# Configure the Distribution node
distribute.inputs["Density"].default_value = 12.5  # ~200 points on a 4x4 plane
distribute.inputs["Seed"].default_value = 0

# Icosphere: subdivision 2 -> 80 faces per pebble
ico_sphere.inputs["Radius"].default_value = 0.2
ico_sphere.inputs["Subdivisions"].default_value = 2

# Random uniform scale
random_scale.data_type = 'FLOAT'
random_scale.inputs["Min"].default_value = 0.08
random_scale.inputs["Max"].default_value = 0.35

# Random rotation vector (Euler angles)
random_rot.data_type = 'VECTOR'
random_rot.inputs["Min"].default_value = (-3.14159, -3.14159, -3.14159)
random_rot.inputs["Max"].default_value = (3.14159, 3.14159, 3.14159)

add_rot.operation = 'ADD'

# Layout (optional, for readability)
group_input.location = (-900, 0)
distribute.location = (-700, 0)
ico_sphere.location = (-700, -200)
random_rot.location = (-700, -300)
add_rot.location = (-500, -150)
instance.location = (-400, 0)
random_scale.location = (-500, -200)
scale_inst.location = (-200, 0)
realize.location = (0, 0)
group_output.location = (200, 0)

# Connect the nodes
links.new(group_input.outputs["Geometry"], distribute.inputs["Geometry"])
links.new(distribute.outputs["Points"], instance.inputs["Points"])
links.new(distribute.outputs["Rotation"], add_rot.inputs[0])
links.new(random_rot.outputs["Value"], add_rot.inputs[1])
links.new(add_rot.outputs["Vector"], instance.inputs["Rotation"])
links.new(ico_sphere.outputs["Mesh"], instance.inputs["Instance"])
links.new(instance.outputs["Instances"], scale_inst.inputs["Geometry"])
links.new(random_scale.outputs["Value"], scale_inst.inputs["Scale"])
links.new(scale_inst.outputs["Geometry"], realize.inputs["Geometry"])
links.new(realize.outputs["Geometry"], group_output.inputs["Geometry"])
