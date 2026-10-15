import bpy
from mathutils import Vector, noise

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Terrain resolution: 120 x 120 faces, exceeding the required 100 x 100 subdivisions
subdivisions = 120
size = 24.0
half_size = size * 0.5

vertices = []
faces = []

def terrain_height(x, y):
    # Layered noise creates broad hills with smaller-scale surface variation
    p1 = Vector((x * 0.075, y * 0.075, 0.0))
    p2 = Vector((x * 0.18, y * 0.18, 13.7))
    p3 = Vector((x * 0.42, y * 0.42, 31.4))

    n1 = noise.noise_vector(p1)[2]
    n2 = noise.noise_vector(p2)[2]
    n3 = noise.noise_vector(p3)[2]

    height = (
        n1 * 3.8 +
        n2 * 1.35 +
        n3 * 0.35
    )

    # Gentle basin-like shaping toward the edges
    radial = ((x / half_size) ** 2 + (y / half_size) ** 2) * 0.45
    return height - radial

# Generate the grid vertices
for row in range(subdivisions + 1):
    y = -half_size + size * row / subdivisions
    for column in range(subdivisions + 1):
        x = -half_size + size * column / subdivisions
        z = terrain_height(x, y)
        vertices.append((x, y, z))

# Generate quad faces
row_width = subdivisions + 1
for row in range(subdivisions):
    for column in range(subdivisions):
        a = row * row_width + column
        b = a + 1
        d = (row + 1) * row_width + column
        c = d + 1
        faces.append((a, b, c, d))

# Create the terrain mesh
mesh = bpy.data.meshes.new("Hilly_Terrain_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

terrain = bpy.data.objects.new("Hilly_Terrain", mesh)
bpy.context.collection.objects.link(terrain)

# Smooth shading for continuous hills
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Simple natural terrain material
material = bpy.data.materials.new("Terrain_Material")
material.diffuse_color = (0.16, 0.32, 0.10, 1.0)
material.roughness = 1.0
terrain.data.materials.append(material)

# Slightly improve the silhouette without changing the required base topology
subsurf = terrain.modifiers.new("Terrain_Smoothing", 'SUBSURF')
subsurf.subdivision_type = 'CATMULL_CLARK'
subsurf.levels = 1
subsurf.render_levels = 1

# Select the generated terrain
bpy.context.view_layer.objects.active = terrain
terrain.select_set(True)
