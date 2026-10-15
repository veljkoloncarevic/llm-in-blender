import bpy
import bmesh
from mathutils import Vector
import random

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 4x4 plane
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "ScatterPlane"

# Create an icosphere to be instanced
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(10, 0, 0))
icosphere = bpy.context.active_object
icosphere.name = "PebbleTemplate"

# Add a Geometry Nodes modifier to the plane
gn_modifier = plane.modifiers.new(name="ScatterPebbles", type='GEOMETRY_NODES')

# Create a new geometry nodes tree
node_tree = bpy.data.node_groups.new(name="ScatterPebbles", type='GeometryNodeTree')
gn_modifier.node_group = node_tree

# Clear default nodes
node_tree.nodes.clear()

# Create nodes
nodes = node_tree.nodes
links = node_tree.links

# Input node
input_node = nodes.new(type='NodeGroupInput')
input_node.location = (0, 0)

# Output node
output_node = nodes.new(type='NodeGroupOutput')
output_node.location = (1000, 0)

# Distribute Points on Faces
distribute_node = nodes.new(type='GeometryNodeDistributePointsOnFaces')
distribute_node.location = (200, 0)
distribute_node.inputs['Density'].default_value = 12.5  # ~200 points on 4x4 plane

# Instance on Points
instance_node = nodes.new(type='GeometryNodeInstanceOnPoints')
instance_node.location = (400, 0)

# Random Value node for size
random_size_node = nodes.new(type='FunctionNodeRandomValue')
random_size_node.location = (200, -200)
random_size_node.inputs['Min'].default_value = 0.08
random_size_node.inputs['Max'].default_value = 0.25
random_size_node.data_type = 'FLOAT'

# Random Value node for rotation (X)
random_rot_x = nodes.new(type='FunctionNodeRandomValue')
random_rot_x.location = (200, -350)
random_rot_x.inputs['Min'].default_value = 0.0
random_rot_x.inputs['Max'].default_value = 6.28
random_rot_x.data_type = 'FLOAT'

# Random Value node for rotation (Y)
random_rot_y = nodes.new(type='FunctionNodeRandomValue')
random_rot_y.location = (200, -450)
random_rot_y.inputs['Min'].default_value = 0.0
random_rot_y.inputs['Max'].default_value = 6.28
random_rot_y.data_type = 'FLOAT'

# Random Value node for rotation (Z)
random_rot_z = nodes.new(type='FunctionNodeRandomValue')
random_rot_z.location = (200, -550)
random_rot_z.inputs['Min'].default_value = 0.0
random_rot_z.inputs['Max'].default_value = 6.28
random_rot_z.data_type = 'FLOAT'

# Combine XYZ for rotation
combine_rot = nodes.new(type='ShaderNodeCombineXYZ')
combine_rot.location = (400, -400)

# Object Info node to get the icosphere
object_info = nodes.new(type='GeometryNodeObjectInfo')
object_info.location = (200, 100)
object_info.inputs['Object'].default_value = icosphere

# Connect nodes
links.new(input_node.outputs['Geometry'], distribute_node.inputs['Geometry'])
links.new(distribute_node.outputs['Points'], instance_node.inputs['Points'])
links.new(object_info.outputs['Geometry'], instance_node.inputs['Instance'])

# Connect size
links.new(random_size_node.outputs['Value'], instance_node.inputs['Scale'])

# Connect rotations
links.new(random_rot_x.outputs['Value'], combine_rot.inputs['X'])
links.new(random_rot_y.outputs['Value'], combine_rot.inputs['Y'])
links.new(random_rot_z.outputs['Value'], combine_rot.inputs['Z'])
links.new(combine_rot.outputs['XYZ'], instance_node.inputs['Rotation'])

# Connect output
links.new(instance_node.outputs['Instances'], output_node.inputs['Geometry'])

# Apply modifier to ensure geometry is generated
bpy.context.view_layer.update()
