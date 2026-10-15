import bpy
import math
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the (p, q) torus knot
p = 2
q = 3
major_radius = 1.0
tube_radius = 0.25

# Resolution parameters to hit target face count (2k - 60k)
# Spline resolution (u_segments) and tube resolution (v_segments)
u_segments = 250  # Number of points along the knot
v_segments = 32   # Resolution of the circular cross-section
# Total faces approx = u_segments * v_segments = 250 * 32 = 8,000 faces (within 2k-60k)

# Generate parametric curve points for a (p,q) torus knot
curve_data = bpy.data.curves.new('TorusKnotCurve', type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = u_segments
curve_data.bevel_depth = tube_radius
curve_data.bevel_resolution = v_segments
curve_data.fill_mode = 'FULL'

spline = curve_data.splines.new(type='POLY')
spline.points.add(u_segments - 1)  # -1 because 1 point exists by default

for i in range(u_segments):
    t = (i / u_segments) * (2.0 * math.pi * q)
    
    # Torus knot equations
    r = major_radius * (1.0 + 0.3 * math.cos(q * t))
    x = r * math.cos(p * t)
    y = r * math.sin(p * t)
    z = 0.4 * major_radius * math.sin(q * t)
    
    # Set point coordinate (w = 1.0 for rational bezier/nurbs, but for poly it's just xyz1)
    # POLY spline points use .co as a 4D vector (x, y, z, w)
    spline.points[i].co = (x, y, z, 1.0)

# Make the curve cyclic to close the knot smoothly
spline.use_cyclic_u = True

# Create curve object
curve_obj = bpy.data.objects.new('TorusKnot', curve_data)
bpy.context.collection.objects.link(curve_obj)

# Smooth shading for the curve object when converted/displayed
curve_obj.data.use_fill_caps = True

# Select and set active
bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)
