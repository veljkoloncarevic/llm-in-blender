import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Radial cross-section profile: (radius, height)
profile = [
    (0.70, 0.00),
    (0.72, 0.015),
    (0.74, 0.035),
    (0.76, 0.08),
    (0.84, 0.16),
    (0.98, 0.30),
    (1.10, 0.50),
    (1.18, 0.75),
    (1.22, 1.02),
    (1.21, 1.28),
    (1.16, 1.52),
    (1.08, 1.72),
    (0.98, 1.90),
    (0.87, 2.06),
    (0.76, 2.20),
    (0.67, 2.34),
    (0.62, 2.48),
    (0.60, 2.68),
    (0.60, 2.90),
    (0.62, 3.04),  # outer lip
    (0.58, 3.08),
    (0.53, 3.08),  # inner lip
    (0.50, 3.02),
    (0.49, 2.88),
    (0.49, 2.68),
    (0.51, 2.50),
    (0.57, 2.34),
    (0.66, 2.20),
    (0.76, 2.06),
    (0.86, 1.90),
    (0.94, 1.70),
    (1.00, 1.48),
    (1.02, 1.24),
    (1.01, 1.00),
    (0.97, 0.76),
    (0.88, 0.54),
    (0.75, 0.35),
    (0.62, 0.22),
    (0.56, 0.16),
    (0.55, 0.10),
    (0.56, 0.055),
    (0.58, 0.025),
    (0.62, 0.00),
]

segments = 128
vertices = []
faces = []

# Build rings around the Z axis
for radius, height in profile:
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        vertices.append((
            radius * math.cos(angle),
            radius * math.sin(angle),
            height
        ))

# Connect adjacent profile rings with quad faces
ring_count = len(profile)
for j in range(ring_count):
    next_j = (j + 1) % ring_count
    for i in range(segments):
        next_i = (i + 1) % segments
        a = j * segments + i
        b = j * segments + next_i
        c = next_j * segments + next_i
        d = next_j * segments + i
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("Vase_Lathe_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

vase = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(vase)
bpy.context.view_layer.objects.active = vase
vase.select_set(True)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Subdivision Surface modifier
subsurf = vase.modifiers.new("Subdivision Surface", 'SUBSURF')
subsurf.subdivision_type = 'CATMULL_CLARK'
subsurf.levels = 2
subsurf.render_levels = 2

# Weighted smooth appearance through autosmooth-compatible normals
mesh.set_sharp_from_angle(angle=math.radians(60.0))
