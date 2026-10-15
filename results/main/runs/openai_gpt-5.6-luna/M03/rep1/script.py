import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Cross-section profile, ordered around the material section:
# bottom center -> exterior -> rim -> interior -> inner bottom center
profile = [
    (0.00, 0.00),
    (0.58, 0.00),
    (0.68, 0.035),
    (0.70, 0.10),
    (0.72, 0.22),
    (0.76, 0.38),
    (0.82, 0.58),
    (0.90, 0.82),
    (0.98, 1.08),
    (1.04, 1.34),
    (1.06, 1.58),
    (1.02, 1.78),
    (0.94, 1.94),
    (0.82, 2.06),
    (0.68, 2.14),
    (0.56, 2.18),
    (0.50, 2.22),
    (0.48, 2.30),
    (0.48, 2.58),
    (0.47, 2.86),
    (0.46, 3.12),
    (0.45, 3.34),
    (0.48, 3.42),  # outer rim
    (0.58, 3.45),
    (0.60, 3.49),
    (0.57, 3.53),  # inner rim
    (0.48, 3.55),
    (0.40, 3.52),
    (0.39, 3.43),
    (0.38, 3.20),
    (0.38, 2.92),
    (0.39, 2.64),
    (0.39, 2.38),
    (0.40, 2.22),
    (0.45, 2.12),
    (0.57, 2.04),
    (0.68, 1.94),
    (0.76, 1.80),
    (0.81, 1.61),
    (0.82, 1.40),
    (0.78, 1.18),
    (0.70, 0.96),
    (0.62, 0.75),
    (0.55, 0.57),
    (0.50, 0.42),
    (0.47, 0.32),
    (0.00, 0.32),
]

segments = 96
vertices = []
rings = []

# Create circular vertex rings for every non-axis profile point
for radius, z in profile:
    if radius == 0.0:
        rings.append(None)
        vertices.append((0.0, 0.0, z))
    else:
        ring = []
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            ring.append(len(vertices))
            vertices.append((
                radius * math.cos(angle),
                radius * math.sin(angle),
                z
            ))
        rings.append(ring)

faces = []

# Connect adjacent profile samples
for p in range(len(profile) - 1):
    ring_a = rings[p]
    ring_b = rings[p + 1]

    if ring_a is not None and ring_b is not None:
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((ring_a[i], ring_a[j], ring_b[j], ring_b[i]))
    elif ring_a is None and ring_b is not None:
        center = vertices.index((0.0, 0.0, profile[p][1]))
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((center, ring_b[i], ring_b[j]))
    elif ring_a is not None and ring_b is None:
        center = vertices.index((0.0, 0.0, profile[p + 1][1]))
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((ring_a[i], center, ring_a[j]))

mesh = bpy.data.meshes.new("Revolved_Vase_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

vase = bpy.data.objects.new("Revolved Vase", mesh)
bpy.context.collection.objects.link(vase)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Subdivision Surface modifier
subdivision = vase.modifiers.new("Subdivision Surface", 'SUBSURF')
subdivision.subdivision_type = 'CATMULL_CLARK'
subdivision.levels = 2
subdivision.render_levels = 2
subdivision.show_viewport = True
subdivision.show_render = True

# Keep the vase selected and active
bpy.context.view_layer.objects.active = vase
vase.select_set(True)
