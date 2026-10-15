import math
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Parameters for (2,3) Torus Knot ---
p = 2
q = 3
major_radius = 2.0
minor_radius = 0.7
tube_radius = 0.25

# Resolution settings to meet the 2,000 - 60,000 face count rule
# Curve resolution (steps along the knot): 250
# Bevel resolution (vertices around the tube): 20
# Total quads roughly = 250 * 20 = 5,000 faces (well within 2k-60k range)
resolution_u = 250
resolution_v = 20

# Create a Curve object
curve_data = bpy.data.curves.new(name="TorusKnotCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = resolution_u
curve_data.bevel_resolution = resolution_v
curve_data.fill_mode = 'FULL'
curve_data.bevel_depth = tube_radius

# Create a Spline in the curve data
polyline = curve_data.splines.new(type='POLY')

# Generate points for the (2,3) torus knot
# Parametric equations:
# x(t) = (R + r * cos(q*t)) * cos(p*t)
# y(t) = (R + r * cos(q*t)) * sin(p*t)
# z(t) = r * sin(q*t)
points = []
for i in range(resolution_u):
    t = (i / resolution_u) * (2.0 * math.pi)
    
    r_cos_qt = minor_radius * math.cos(q * t)
    x = (major_radius + r_cos_qt) * math.cos(p * t)
    y = (major_radius + r_cos_qt) * math.sin(p * t)
    z = minor_radius * math.sin(q * t)
    
    points.append((x, y, z))

# Set the points on the polyline
# The first point is already created by default, so we resize and set coordinates.
polyline.points.add(len(points) - 1)
for i, coord in enumerate(points):
    polyline.points[i].co = (coord[0], coord[1], coord[2], 1.0)

# Make the curve cyclic (closed loop)
polyline.use_cyclic_u = True

# Create the curve object in the scene
curve_obj = bpy.data.objects.new("TorusKnot", curve_data)
bpy.context.collection.objects.link(curve_obj)

# Optional: Convert to mesh to ensure exact face count and apply modifiers if needed,
# though curve with bevel depth generates clean geometry automatically.
bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)

# Convert curve to mesh to guarantee geometry structure
bpy.ops.object.convert(target='MESH')

# Smooth shading for the tube mesh
mesh_obj = bpy.context.active_object
for polygon in mesh_obj.data.polygons:
    polygon.use_smooth = True
