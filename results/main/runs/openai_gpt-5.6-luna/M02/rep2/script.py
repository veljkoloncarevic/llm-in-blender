import bpy
import math
from mathutils import Vector
from mathutils.noise import noise

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Terrain resolution: 120 x 120 faces, 121 x 121 vertices
subdivisions = 120
size = 24.0
step = size / subdivisions

vertices = []
faces = []

def terrain_height(x, y):
    # Layered procedural noise for broad hills and smaller detail
    p = Vector((x * 0.075, y * 0.075, 0.0))
    broad = noise(p, noise_basis='PERLIN_ORIGINAL')
    medium = noise(p * 2.4 + Vector((17.3, -9.1, 4.7)),
                   noise_basis='PERLIN_ORIGINAL')
    detail = noise(p * 6.0 + Vector((-5.2, 13.7, 21.4)),
                   noise_basis='PERLIN_ORIGINAL')

    height = (
        broad * 4.2 +
        medium * 1.35 +
        detail * 0.35
    )

    # Gentle falloff near the outer boundary
    edge_distance = min(
        (size * 0.5 - abs(x)) / (size * 0.5),
        (size * 0.5 - abs(y)) / (size * 0.5)
    )
    edge_factor = min(1.0, max(0.0, edge_distance * 5.0))

    return height * (0.75 + 0.25 * edge_factor)

# Create the grid vertices
for row in range(subdivisions + 1):
    y = -size * 0.5 + row * step
    for column in range(subdivisions + 1):
        x = -size * 0.5 + column * step
        z = terrain_height(x, y)
        vertices.append((x, y, z))

# Create quad faces
row_width = subdivisions + 1
for row in range(subdivisions):
    for column in range(subdivisions):
        a = row * row_width + column
        b = a + 1
        d = (row + 1) * row_width + column
        c = d + 1
        faces.append((a, b, c, d))

# Build the mesh
mesh = bpy.data.meshes.new("Procedural_Hilly_Terrain")
mesh.from_pydata(vertices, [], faces)
mesh.update()

terrain = bpy.data.objects.new("Hilly_Terrain", mesh)
bpy.context.collection.objects.link(terrain)

# Smooth shading for a natural terrain appearance
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Add a simple terrain material
material = bpy.data.materials.new("Terrain_Material")
material.diffuse_color = (0.22, 0.38, 0.12, 1.0)
terrain.data.materials.append(material)

# Make the terrain the active object
bpy.context.view_layer.objects.active = terrain
terrain.select_set(True)
