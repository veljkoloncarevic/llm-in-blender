import bpy
import bmesh
from mathutils import noise
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new mesh and object
mesh = bpy.data.meshes.new("Terrain")
terrain_obj = bpy.data.objects.new("Terrain", mesh)
bpy.context.collection.objects.link(terrain_obj)
bpy.context.view_layer.objects.active = terrain_obj
terrain_obj.select_set(True)

# Create BMesh
bm = bmesh.new()

# Parameters for terrain generation
grid_size = 110  # 110x110 grid = 12,100 vertices, ~24,000 faces
scale = 0.5  # Spacing between vertices
height_scale = 2.0  # Height variation
noise_scale = 0.1  # Noise frequency

# Generate vertices with noise-based heights
vertices = []
for y in range(grid_size):
    row = []
    for x in range(grid_size):
        # Calculate world position
        world_x = x * scale
        world_y = y * scale
        
        # Use Perlin noise for natural-looking terrain
        # Combine multiple noise octaves for more detail
        height = 0
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0
        
        for octave in range(3):
            noise_val = noise.noise(
                (world_x * noise_scale * frequency,
                 world_y * noise_scale * frequency,
                 octave * 0.5)
            )
            height += noise_val * amplitude
            max_amplitude += amplitude
            amplitude *= 0.5
            frequency *= 2.0
        
        height = (height / max_amplitude) * height_scale
        
        # Create vertex
        vert = bm.verts.new((world_x, world_y, height))
        row.append(vert)
    vertices.append(row)

# Ensure lookup table is built
bm.verts.ensure_lookup_table()

# Generate faces (quads)
for y in range(grid_size - 1):
    for x in range(grid_size - 1):
        # Get four vertices for this quad
        v0 = vertices[y][x]
        v1 = vertices[y][x + 1]
        v2 = vertices[y + 1][x + 1]
        v3 = vertices[y + 1][x]
        
        # Create quad face
        try:
            bm.faces.new([v0, v1, v2, v3])
        except ValueError:
            # If face creation fails, create two triangles instead
            try:
                bm.faces.new([v0, v1, v2])
                bm.faces.new([v0, v2, v3])
            except ValueError:
                pass

# Write BMesh to mesh
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Apply smooth shading for better appearance
bpy.context.view_layer.objects.active = terrain_obj
bpy.ops.object.shade_smooth()

# Print statistics
print(f"Terrain generated:")
print(f"  Vertices: {len(mesh.vertices)}")
print(f"  Faces: {len(mesh.polygons)}")
print(f"  Grid size: {grid_size}x{grid_size}")
