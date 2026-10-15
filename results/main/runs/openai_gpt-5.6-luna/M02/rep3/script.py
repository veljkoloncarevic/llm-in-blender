import bpy
from mathutils import Vector, noise

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Terrain resolution: 100 x 100 quad faces
grid_x = 100
grid_y = 100
size_x = 40.0
size_y = 40.0

vertices = []
faces = []

def terrain_height(x, y):
    # Layered procedural Perlin noise for broad hills and smaller surface variation
    broad = noise.noise_vector(
        Vector((x * 0.075, y * 0.075, 0.0))
    )[0]
    medium = noise.noise_vector(
        Vector((x * 0.16 + 31.7, y * 0.16 - 12.4, 4.0))
    )[1]
    detail = noise.noise_vector(
        Vector((x * 0.42 - 8.2, y * 0.42 + 19.6, 11.0))
    )[2]

    # Make the broad component dominate to create rolling hills
    return broad * 6.5 + medium * 2.0 + detail * 0.55

# Generate the terrain vertices
for iy in range(grid_y + 1):
    y = (iy / grid_y - 0.5) * size_y
    for ix in range(grid_x + 1):
        x = (ix / grid_x - 0.5) * size_x
        z = terrain_height(x, y)
        vertices.append((x, y, z))

# Generate quad faces
row_width = grid_x + 1
for iy in range(grid_y):
    for ix in range(grid_x):
        a = iy * row_width + ix
        b = a + 1
        d = (iy + 1) * row_width + ix
        c = d + 1
        faces.append((a, b, c, d))

# Create mesh and object
mesh = bpy.data.meshes.new("Procedural_Hilly_Terrain")
mesh.from_pydata(vertices, [], faces)
mesh.update()

terrain = bpy.data.objects.new("Procedural Hilly Terrain", mesh)
bpy.context.collection.objects.link(terrain)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Slightly improve the visual terrain normals
mesh.set_sharp_from_angle(angle=0.785398)

# Select the generated terrain
bpy.context.view_layer.objects.active = terrain
terrain.select_set(True)
