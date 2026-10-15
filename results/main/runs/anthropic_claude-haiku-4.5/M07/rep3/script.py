import bpy
import bmesh
from mathutils import Vector
from random import random, seed

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set random seed for reproducibility
seed(42)

# Create base plane (4x4)
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "ScatterPlane"

# Create icosphere pebble template
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(10, 10, 0))
pebble = bpy.context.active_object
pebble.name = "PebbleMaster"

# Convert to icosphere by using a bmesh operation for better geometry
bpy.context.view_layer.objects.active = pebble
bpy.ops.object.shade_smooth()

# Create geometry nodes modifier on the plane
plane_obj = bpy.data.objects["ScatterPlane"]
bpy.context.view_layer.objects.active = plane_obj

# Add geometry nodes modifier
geom_modifier = plane_obj.modifiers.new(name="ScatterPebbles", type='GEOMETRY')
geom_modifier.node_group = bpy.data.node_groups.new(name="PebbleScatter", type='GEOMETRY')

# Get the node group
node_group = geom_modifier.node_group
node_group.use_fake_user = True

# Clear default nodes
node_group.nodes.clear()

# Create nodes
nodes = node_group.nodes
links = node_group.links

# Input and Output nodes
input_node = nodes.new(type='NodeGroupInput')
output_node = nodes.new(type='NodeGroupOutput')

# Add sockets to node group
node_group.inputs.new('NodeSocketGeometry', 'Geometry')
node_group.outputs.new('NodeSocketGeometry', 'Geometry')

# Distribute Points on Faces
distribute_node = nodes.new(type='GeometryNodeDistributePointsOnFaces')
distribute_node.use_legacy_behavior = False

# Instance on Points
instance_node = nodes.new(type='GeometryNodeInstanceOnPoints')

# Object Info node for pebble reference
obj_info_node = nodes.new(type='GeometryNodeObjectInfo')
obj_info_node.inputs['Object'].default_value = pebble

# Random Value nodes for size variation
random_size_node = nodes.new(type='FunctionNodeRandomValue')
random_size_node.inputs['Min'].default_value = 0.05
random_size_node.inputs['Max'].default_value = 0.15

# Random Value node for rotation
random_rot_node = nodes.new(type='FunctionNodeRandomValue')
random_rot_node.inputs['Min'].default_value = 0.0
random_rot_node.inputs['Max'].default_value = 1.0

# Scale node for size
scale_node = nodes.new(type='GeometryNodeScale')
scale_node.inputs['Scale'].default_value = (1.0, 1.0, 1.0)

# Rotation to Euler node
rot_euler_node = nodes.new(type='FunctionNodeRotateEuler')

# Connect nodes
links.new(input_node.outputs['Geometry'], distribute_node.inputs['Mesh'])
links.new(distribute_node.outputs['Points'], instance_node.inputs['Points'])
links.new(obj_info_node.outputs['Geometry'], scale_node.inputs['Geometry'])
links.new(scale_node.outputs['Geometry'], instance_node.inputs['Instance'])

# Connect size randomization
links.new(distribute_node.outputs['Points'], random_size_node.inputs['ID'])
links.new(random_size_node.outputs['Value'], instance_node.inputs['Scale'])

# Connect rotation randomization
links.new(distribute_node.outputs['Points'], random_rot_node.inputs['ID'])
links.new(random_rot_node.outputs['Value'], rot_euler_node.inputs['Rotation'])
links.new(rot_euler_node.outputs['Rotation'], instance_node.inputs['Rotation'])

# Connect instance to output
links.new(instance_node.outputs['Instances'], output_node.inputs['Geometry'])

# Configure distribute points node for ~200 points
distribute_node.inputs['Density'].default_value = 12.5

# Hide the pebble master object
pebble.hide_set(True)
pebble.hide_render = True

# Select plane and ensure it's active
plane_obj.select_set(True)
bpy.context.view_layer.objects.active = plane_obj

print("Scene created successfully with scattered pebbles using Geometry Nodes")
