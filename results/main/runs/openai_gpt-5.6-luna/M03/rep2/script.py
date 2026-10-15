import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Vase profile: (radius, height)
profile = []

# Flat exterior base and body
profile.append((0.0, 0.0))
profile.append((1.22, 0.0))
profile.append((1.38, 0.06))
profile.append((1.48, 0.16))
profile.append((1.55, 0.35))

# Outer body profile
outer_samples = [
    (1.58, 0.65),
    (1.62, 1.00),
    (1.66, 1.40),
    (1.68, 1.80),
    (1.67, 2.20),
    (1.64, 2.60),
    (1.59, 2.95),
    (1.52, 3.25),
    (1.43, 3.50),
    (1.31, 3.72),
    (1.16, 3.92),
    (1.00, 4.08),
    (0.84, 4.22),
    (0.73, 4.34),
    (0.68, 4.48),
    (0.67, 4.72),
    (0.67, 4.98),
    (0.67, 5.20),
]
profile.extend(outer_samples)

# Thick rounded lip
profile.extend([
    (0.65, 5.28),
    (0.61, 5.33),
    (0.57, 5.34),
])

# Interior profile, descending from the opening
inner_samples = [
    (0.54, 5.24),
    (0.54, 5.02),
    (0.54, 4.76),
    (0.55, 4.50),
    (0.60, 4.34),
    (0.71, 4.20),
    (0.84, 4.04),
    (0.97, 3.88),
    (1.09, 3.68),
    (1.20, 3.46),
    (1.29, 3.20),
    (1.35, 2.90),
    (1.39, 2.55),
    (1.42, 2.15),
    (1.41, 1.75),
    (1.38, 1.35),
    (1.33, 0.98),
    (1.25, 0.68),
    (1.12, 0.46),
    (0.88, 0.32),
    (0.48, 0.27),
]
profile.extend(inner_samples)
profile.append((0.0, 0.27))

# Build lathed mesh
segments = 64
vertices = []
faces = []

for i in range(segments):
    angle = 2.0 * math.pi * i / segments
    ca = math.cos(angle)
    sa = math.sin(angle)
    for radius, height in profile:
        vertices.append((radius * ca, radius * sa, height))

profile_count = len(profile)

for i in range(segments):
    ni = (i + 1) % segments
    for j in range(profile_count - 1):
        a = i * profile_count + j
        b = ni * profile_count + j
        c = ni * profile_count + j + 1
        d = i * profile_count + j + 1
        faces.append((a, b, c, d))

mesh = bpy.data.meshes.new("Vase_Lathe_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

vase = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(vase)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Subdivision surface
subsurf = vase.modifiers.new("Subdivision Surface", 'SUBSURF')
subsurf.subdivision_type = 'CATMULL_CLARK'
subsurf.levels = 2
subsurf.render_levels = 2

# Select the vase
bpy.context.view_layer.objects.active = vase
vase.select_set(True)
