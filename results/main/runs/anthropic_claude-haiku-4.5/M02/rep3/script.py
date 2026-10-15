import bpy
import bmesh
from mathutils import Vector, noise
import random

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set random seed for reproducibility
random.seed(42)

# Create a plane mesh
mesh = bpy.data.meshes.new("Terrain")
obj = bpy.data.objects.new("Terrain", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Use bmesh to create the terrain
bm = bmesh.new()

# Grid parameters
grid_size = 120  # 120x120 grid = 14,400 faces (within 5k-120k range)
scale = 0.5  # Spacing between vertices
height_scale = 5.0  # Height variation

# Create vertices with noise-based heights
vertices = []
for y in range(grid_size + 1):
    row = []
    for x in range(grid_size + 1):
        # Use Perlin noise for natural-looking terrain
        # Scale coordinates for noise function
        nx = x * 0.05
        ny = y * 0.05
        
        # Get noise value (range approximately -1 to 1)
        height = noise.noise(Vector((nx, ny, 0))) * height_scale
        
        # Add additional noise octave for more detail
        height += noise.noise(Vector((nx * 2, ny * 2, 1))) * height_scale * 0.5
        
        # Create vertex position
        pos = Vector((x * scale, y * scale, height))
        vert = bm.verts.new(pos)
        row.append(vert)
    vertices.append(row)

# Ensure lookup table is built
bm.verts.ensure_lookup_table()

# Create faces (quads) from the grid
for y in range(grid_size):
    for x in range(grid_size):
        v0 = vertices[y][x]
        v1 = vertices[y][x + 1]
        v2 = vertices[y + 1][x + 1]
        v3 = vertices[y + 1][x]
        
        # Create quad face
        bm.faces.new([v0, v1, v2, v3])

# Write bmesh to mesh
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Apply smooth shading for better appearance
bpy.context.view_layer.objects.active = obj
bpy.ops.object.shade_smooth()

# Center the object at origin
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

print(f"Terrain created with {len(mesh.vertices)} vertices and {len(mesh.polygons)} faces")
