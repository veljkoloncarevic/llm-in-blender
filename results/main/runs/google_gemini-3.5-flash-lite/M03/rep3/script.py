import bpy
import mathutils

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define a profile curve for a vase (X, Z coordinates)
# Narrow neck, wide body, flat base
profile_points = [
    (0.0, 0.0),    # Center bottom (flat base start)
    (0.8, 0.0),    # Outer bottom edge
    (0.9, 0.1),    # Lower curve start
    (1.4, 0.6),    # Widest part of the belly
    (1.0, 1.3),    # Tapering inward toward shoulder
    (0.4, 1.8),    # Narrow neck start
    (0.35, 2.3),   # Neck middle
    (0.5, 2.5),    # Flared lip outer edge
    (0.4, 2.55),   # Lip top
    (0.25, 2.5)    # Lip inner rim
]

# 3. Create a Curve object using a Bezier or Poly curve to revolve
curve_data = bpy.data.curves.new('VaseProfile', type='CURVE')
curve_data.dimensions = '2D'
curve_data.resolution_u = 6

spline = curve_data.splines.new(type='POLY')
spline.points.add(len(profile_points) - 1)

for i, (x, z) in enumerate(profile_points):
    # Poly spline points use a 4D vector (X, Y, Z, W)
    spline.points[i].co = (x, 0.0, z, 1.0)

# Create the object from the curve
profile_obj = bpy.data.objects.new('VaseProfileObj', curve_data)
bpy.context.collection.objects.link(profile_obj)

# 4. Add Screw Modifier to revolve the profile around Z-axis
screw_mod = profile_obj.modifiers.new(name='VaseScrew', type='SCREW')
screw_mod.axis = 'Z'
screw_mod.angle = 3.14159 * 2.0
# Set steps to achieve target face count (approx 48 steps * profile points * 2 for subsurf)
screw_mod.steps = 48
screw_mod.render_steps = 48
screw_mod.use_smooth_shade = True
screw_mod.use_merge_vertices = True
screw_mod.merge_threshold = 0.001

# Convert the curve with modifiers to a Mesh object
depsgraph = bpy.context.evaluated_depsgraph_get()
evaluated_obj = profile_obj.evaluated_get(depsgraph)
mesh = bpy.data.meshes.new_from_object(evaluated_obj)

vase_obj = bpy.data.objects.new('Vase', mesh)
bpy.context.collection.objects.link(vase_obj)

# Clean up the original profile object
bpy.data.objects.remove(profile_obj)
bpy.data.curves.remove(curve_data)

# 5. Post-process the mesh: set smooth shading and add Subdivision Surface
bpy.context.view_layer.objects.active = vase_obj
vase_obj.select_set(True)

# Ensure smooth shading on all faces
for polygon in vase_obj.data.polygons:
    polygon.use_smooth = True

# Add Subdivision Surface modifier for high fidelity and smooth finish
subsurf_mod = vase_obj.modifiers.new(name='VaseSubsurf', type='SUBSURF')
subsurf_mod.levels = 2
subsurf_mod.render_levels = 2

# Optional: Add Solidify or rely on the profile thickness (profile already has thickness via lip)
