import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the coil spring
turns = 8
radius = 1.0
height = 4.0
wire_radius = 0.1
resolution_turns = 32  # Segments per turn (vertices along the helix path)
resolution_wire = 12   # Segments for the circular cross-section of the wire

total_path_verts = turns * resolution_turns

# Create curve data for the helix
curve_data = bpy.data.curves.new('SpringCurve', type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = resolution_turns

spline = curve_data.splines.new(type='POLY')
spline.points.add(total_path_verts - 1)

# Generate helix coordinates
for i in range(total_path_verts):
    t = i / (resolution_turns - 1)  # goes from 0 to turns
    angle = t * 2.0 * math.pi * (turns / (turns if resolution_turns == 0 else 1)) # Wait, let's do it precisely:
    
# Let's rewrite the point loop correctly:
# We want 'turns' full rotations over the height.
# i goes from 0 to total_path_verts - 1.
# max t = turns.
for i in range(total_path_verts):
    fraction = i / resolution_turns
    angle = fraction * 2.0 * math.pi
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = (i / total_path_verts) * height
    
    # Set coordinates (w = 1.0 for homogeneous)
    spline.points[i].co = (x, y, z, 1.0)

# Set up bevel for the curve to make it a swept tube (circular wire cross-section)
curve_data.bevel_depth = wire_radius
curve_data.bevel_resolution = resolution_wire
curve_data.fill_mode = 'FULL'

# Create object from curve
curve_obj = bpy.data.objects.new('CoilSpring', curve_data)
bpy.context.collection.objects.link(curve_obj)

# Convert to mesh to ensure exact face count and structure
bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)
bpy.ops.object.convert(target='MESH')

# Verify mesh and face count (should be well within 2,000 to 60,000 range)
# total_path_verts * resolution_wire * 2 approximately
mesh = curve_obj.data
print(f"Spring generated with {len(mesh.polygons)} faces and {len(mesh.vertices)} vertices.")
