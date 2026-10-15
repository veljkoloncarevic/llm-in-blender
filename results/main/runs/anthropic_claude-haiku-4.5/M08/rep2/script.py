import bpy
import bmesh
from mathutils import Vector
import math

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters for the coil spring
turns = 8
radius = 1.0
height = 4.0
wire_radius = 0.15
segments_per_turn = 32
vertical_segments = turns * segments_per_turn

# Create the helix curve (centerline of the spring)
curve_data = bpy.data.curves.new(name="SpringCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 12

polyline = curve_data.splines.new('POLY')
polyline.points.add(vertical_segments)

# Generate helix points
for i in range(vertical_segments + 1):
    t = i / vertical_segments
    angle = t * turns * 2 * math.pi
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = t * height
    
    if i < len(polyline.points):
        polyline.points[i].co = (x, y, z, 1.0)

# Create a circle curve for the bevel object (wire cross-section)
bevel_curve_data = bpy.data.curves.new(name="BevelCircle", type='CURVE')
bevel_curve_data.dimensions = '3D'
bevel_curve_data.resolution_u = 12

bevel_spline = bevel_curve_data.splines.new('BEZIER')
bevel_spline.use_cyclic_u = True
bevel_spline.points.add(3)

# Create a circle in the XY plane
circle_points = [
    (wire_radius, 0, 0),
    (0, wire_radius, 0),
    (-wire_radius, 0, 0),
    (0, -wire_radius, 0),
]

for i in range(4):
    pt = bevel_spline.points[i % 4]
    pt.co = (circle_points[i][0], circle_points[i][1], circle_points[i][2], 1.0)
    pt.handle_left_type = 'AUTO'
    pt.handle_right_type = 'AUTO'

# Add extra point for cyclic curve
bevel_spline.points.add(1)
bevel_spline.points[4].co = (wire_radius, 0, 0, 1.0)

# Assign the bevel curve to the helix curve
curve_data.bevel_object = bpy.data.objects.new("BevelObject", bevel_curve_data)
bpy.context.collection.objects.link(bevel_curve_data.objects[0] if hasattr(bevel_curve_data, 'objects') else bpy.data.objects[-1])

# Create bevel object
bevel_obj = bpy.data.objects.new("BevelObject", bevel_curve_data)
bpy.context.collection.objects.link(bevel_obj)
curve_data.bevel_object = bevel_obj

# Create the spring object
spring_obj = bpy.data.objects.new("Spring", curve_data)
bpy.context.collection.objects.link(spring_obj)
bpy.context.view_layer.objects.active = spring_obj
spring_obj.select_set(True)

# Set curve properties for better geometry
curve_data.resolution_u = 12
curve_data.bevel_depth = wire_radius
curve_data.bevel_resolution = 8

# Convert curve to mesh to get face count in the desired range
bpy.ops.object.convert(target='MESH')

# Get the resulting mesh
mesh = spring_obj.data
print(f"Total vertices: {len(mesh.vertices)}")
print(f"Total faces: {len(mesh.polygons)}")
print(f"Total edges: {len(mesh.edges)}")
