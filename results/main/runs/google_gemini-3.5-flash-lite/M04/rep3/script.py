import bpy
import math
import mathutils

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Parameters for (2,3) Torus Knot ---
p = 2
q = 3
major_radius = 2.0
minor_radius = 0.8
tube_radius = 0.25

# Resolution settings to target between 2,000 and 60,000 faces
# A tube with resolution U = 300 (along the knot) and V = 16 (cross-section)
# will have 300 * 16 = 4,800 quads (well within the 2k-60k range).
resolution_u = 300
resolution_v = 16

# Generate the parametric curve points for the torus knot
curve_points = []
for i in range(resolution_u):
    u = (i / resolution_u) * (2.0 * math.pi * p)
    
    # Torus knot parametric equations
    r = major_radius + minor_radius * math.cos(q * u / p)
    x = r * math.cos(u)
    y = r * math.sin(u)
    z = minor_radius * math.sin(q * u / p)
    
    curve_points.append(mathutils.Vector((x, y, z)))

# Create a Curve data-block and a Spline
curve_data = bpy.data.curves.new(name="TorusKnotCurve", type='CURVE')
curve_data.dimensions = '3D'
curve_data.resolution_u = 4

# Create a NURBS or Poly spline. Using Poly with high resolution gives precise control
spline = curve_data.splines.new(type='POLY')
spline.points.add(len(curve_points) - 1)

for idx, coord in enumerate(curve_points):
    # Poly spline points require a 4-tuple (x, y, z, w)
    spline.points[idx].co = (coord.x, coord.y, coord.z, 1.0)

# Make the curve cyclic to close the knot smoothly
spline.use_cyclic_u = True

# Add bevel depth to turn it into a tube
curve_data.bevel_depth = tube_radius
curve_data.bevel_resolution = resolution_v

# Create the curve object and link to scene
curve_obj = bpy.data.objects.new("TorusKnotObject", curve_data)
bpy.context.collection.objects.link(curve_obj)

# Convert curve to mesh to satisfy the "swept mesh / face count" condition explicitly
bpy.context.view_layer.objects.active = curve_obj
bpy.ops.object.convert(target='MESH')

# Smooth the resulting mesh normals
mesh = curve_obj.data
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Optional: Add a subtle material so it looks good if evaluated visually
mat = bpy.data.materials.new(name="KnotMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.05, 0.4, 0.8, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.2
    bsdf.inputs['Metallic'].default_value = 0.5

curve_obj.data.materials.append(mat)
