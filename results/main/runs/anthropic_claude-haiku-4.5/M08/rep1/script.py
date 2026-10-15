import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
turns = 8
radius = 1.0
height = 4.0
wire_radius = 0.15
segments_per_turn = 64
wire_segments = 24

# Create helix curve
curve_data = bpy.data.curves.new(name="HelixCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 12

# Create spline
spline = curve_data.splines.new(type='BEZIER')
spline.use_smooth = True

# Calculate number of points needed
total_points = turns * segments_per_turn + 1
spline.points.add(total_points - 1)

# Generate helix points
for i in range(total_points):
    t = i / (total_points - 1)
    angle = t * turns * 2 * math.pi
    z = t * height
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    
    point = spline.points[i]
    point.co = (x, y, z, 1.0)

# Create circle for bevel
circle_curve_data = bpy.data.curves.new(name="WireCircle", type='CURVE')
circle_curve_data.dimensions = '3D'
circle_spline = circle_curve_data.splines.new(type='BEZIER')
circle_spline.use_smooth = True

# Create circle points
circle_points = wire_segments
circle_spline.points.add(circle_points)

for i in range(circle_points):
    angle = (i / circle_points) * 2 * math.pi
    x = wire_radius * math.cos(angle)
    y = wire_radius * math.sin(angle)
    point = circle_spline.points[i]
    point.co = (x, y, 0, 1.0)

# Close the circle
circle_spline.use_cyclic_u = True

# Create objects
helix_obj = bpy.data.objects.new("Helix", curve_data)
circle_obj = bpy.data.objects.new("WireCircle", circle_curve_data)

# Link to scene
scene = bpy.context.scene
scene.collection.objects.link(helix_obj)
scene.collection.objects.link(circle_obj)

# Set bevel object
curve_data.bevel_object = circle_obj

# Convert to mesh for final result
bpy.context.view_layer.objects.active = helix_obj
helix_obj.select_set(True)

# Apply modifiers by converting curve to mesh
bpy.ops.object.convert(target='MESH')

# Verify face count
mesh = helix_obj.data
face_count = len(mesh.polygons)

# Clean up circle object
bpy.data.objects.remove(circle_obj, do_unlink=True)
bpy.data.curves.remove(circle_curve_data, do_unlink=True)
