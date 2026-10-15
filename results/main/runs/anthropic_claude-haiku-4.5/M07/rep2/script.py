import bpy
import bmesh
from mathutils import Vector, Euler
import random

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4x4 plane
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "ScatterPlane"

# Create an icosphere template (will be instanced)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(10, 10, 10))
icosphere = bpy.context.active_object
icosphere.name = "PebbleTemplate"

# Hide the template from viewport and rendering
icosphere.hide_set(True)
icosphere.hide_render = True

# Select the plane to add geometry nodes
bpy.context.view_layer.objects.active = plane
plane.select_set(True)

# Add a Geometry Nodes modifier to the plane
gn_modifier = plane.modifiers.new(name="ScatterPebbles", type='GEOMETRY_NODES')

# Create a new geometry nodes tree
geo_nodes_tree = bpy.data.node_groups.new(name="PebbleScatter", type='GeometryNodeTree')
gn_modifier.node_group = geo_nodes_tree

# Create the node tree
nodes = geo_nodes_tree.nodes
links = geo_nodes_tree.links
nodes.clear()

# Create input node
group_input = nodes.new(type='NodeGroupInput')
group_input.location = (0, 0)

# Create output node
group_output = nodes.new(type='NodeGroupOutput')
group_output.location = (1200, 0)

# Distribute Points on Faces node
distribute_node = nodes.new(type='GeometryNodeDistributePointsOnFaces')
distribute_node.location = (200, 0)
distribute_node.inputs['Density'].default_value = 12.5  # ~200 points on 4x4 plane

# Random Value node for size variation
random_size = nodes.new(type='GeometryNodeRandomValue')
random_size.location = (400, 200)
random_size.inputs['Min'].default_value = 0.05
random_size.inputs['Max'].default_value = 0.15
random_size.data_type = 'FLOAT'

# Random Value node for rotation
random_rotation = nodes.new(type='GeometryNodeRandomValue')
random_rotation.location = (400, 400)
random_rotation.inputs['Min'].default_value = 0.0
random_rotation.inputs['Max'].default_value = 1.0
random_rotation.data_type = 'FLOAT_VECTOR'

# Instance on Points node
instance_node = nodes.new(type='GeometryNodeInstanceOnPoints')
instance_node.location = (700, 100)

# Object Info node to get the icosphere
object_info = nodes.new(type='GeometryNodeObjectInfo')
object_info.location = (500, -200)
object_info.inputs['Object'].default_value = icosphere

# Scale node for size variation
scale_node = nodes.new(type='GeometryNodeScale')
scale_node.location = (600, -200)
scale_node.inputs['Scale'].default_value = 0.1

# Rotate Euler node for rotation
rotate_node = nodes.new(type='GeometryNodeRotateEuler')
rotate_node.location = (600, -100)
rotate_node.space = 'OBJECT'

# Connect nodes
links.new(group_input.outputs['Geometry'], distribute_node.inputs['Mesh'])
links.new(distribute_node.outputs['Points'], instance_node.inputs['Points'])

# Connect random size
links.new(random_size.outputs['Value'], scale_node.inputs['Scale'])
links.new(scale_node.outputs['Geometry'], instance_node.inputs['Instance'])

# Connect object info
links.new(object_info.outputs['Geometry'], scale_node.inputs['Geometry'])

# Connect rotation
links.new(random_rotation.outputs['Value'], rotate_node.inputs['Rotation'])
links.new(object_info.outputs['Geometry'], rotate_node.inputs['Geometry'])
links.new(rotate_node.outputs['Geometry'], instance_node.inputs['Instance'])

# Connect to output
links.new(instance_node.outputs['Instances'], group_output.inputs['Geometry'])

# Ensure the plane is selected and modifier is applied
plane.select_set(True)
bpy.context.view_layer.objects.active = plane
