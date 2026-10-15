import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1. Create a 4x4 plane
bpy.ops.mesh.primitive_plane_size(size=4.0, enter_editmode=False, align='WORLD', location=(0, 0, 0))
plane = bpy.context.active_object
plane.name = "PebblePlane"

# 2. Create the pebble mesh (icosphere)
# Subdivision level 3 gives 1280 faces per pebble.
# 1280 * 200 = 256,000 max, but we want 5k-150k. Let's use subdivision level 2 (320 faces * 200 = 64,000 faces, perfectly in range).
bpy.ops.mesh.primitive_ico_sphere_add(radius=0.1, subdivisions=2, location=(0, 0, -10))
pebble = bpy.context.active_object
pebble.name = "PebbleTemplate"

# 3. Add Geometry Nodes modifier to the plane
mod = plane.modifiers.new(name="PebbleScatter", TYPE='NODES')
node_group = bpy.data.node_groups.new(name="PebbleScatterNodeGroup", type='GeometryNodeTree')
mod.node_group = node_group

nodes = node_group.nodes
links = node_group.links

# Clear default nodes
nodes.clear()

# Create nodes
node_group_input = nodes.new(type='NodeGroupInput')
node_group_input.location = (-400, 0)

node_group_output = nodes.new(type='NodeGroupOutput')
node_group_output.location = (900, 0)

node_distribute = nodes.new(type='GeometryNodeDistributePointsOnFaces')
node_distribute.location = (-100, 0)
# Set distribution mode to Poisson Disk for better spacing, or Random. Let's use Random for exact count control.
node_distribute.mode = 'RANDOM'
# Set point count to ~200
node_distribute.inputs['Density Max'].default_value = 50.0  # Just a fallback, let's use Count if available, or set density. 
# In newer Blender versions, Distribute Points on Faces uses Density. Let's set Count via Random Value or use 'Count' input if exposed.
# Actually, standard 'Distribute Points on Faces' has a 'Density' input. To set an exact count, we can plug a Random Value or integer into a Count socket if available, 
# but Blender's Distribute node uses Density. Let's set Density such that ~200 points are generated on a 4x4 (16 sq m) area -> Density ~ 12.5.
node_distribute.inputs['Density'].default_value = 12.5
node_distribute.inputs['Seed'].default_value = 42

node_instance = nodes.new(type='GeometryNodeInstanceOnPoints')
node_instance.location = (300, 0)

node_object_info = nodes.new(type='GeometryNodeObjectInfo')
node_object_info.location = (0, -200)
node_object_info.inputs['Object'].default_value = pebble
node_object_info.transform_space = 'RELATIVE'

node_random_scale = nodes.new(type='FunctionNodeRandomValue')
node_random_scale.location = (50, -200)
node_random_scale.data_type = 'FLOAT_VECTOR'
node_random_scale.inputs['Min'].default_value = (0.5, 0.5, 0.5)
node_random_scale.inputs['Max'].default_value = (1.5, 1.5, 1.5)

node_random_rot = nodes.new(type='FunctionNodeRandomValue')
node_random_rot.location = (50, -400)
node_random_rot.data_type = 'FLOAT_VECTOR'
node_random_rot.inputs['Min'].default_value = (0.0, 0.0, 0.0)
node_random_rot.inputs['Max'].default_value = (6.28318, 6.28318, 6.28318)

# Connect nodes
# Group Input (Geometry) -> Distribute Points
links.new(node_group_input.outputs['Geometry'], node_distribute.inputs['Mesh'])

# Distribute Points (Points) -> Instance on Points (Points)
links.new(node_distribute.outputs['Points'], node_instance.inputs['Points'])

# Object Info (Geometry) -> Instance on Points (Instance)
links.new(node_object_info.outputs['Geometry'], node_instance.inputs['Instance'])

# Random Scale -> Instance on Points (Scale)
links.new(node_random_scale.outputs['Value'], node_instance.inputs['Scale'])

# Random Rotation -> Instance on Points (Rotation)
links.new(node_random_rot.outputs['Value'], node_instance.inputs['Rotation'])

# Instance on Points (Instances) -> Group Output (Geometry)
links.new(node_instance.outputs['Instances'], node_group_output.inputs['Geometry'])

# Hide the pebble template from view/render so only instances show
pebble.hide_viewport = True
pebble.hide_render = True
