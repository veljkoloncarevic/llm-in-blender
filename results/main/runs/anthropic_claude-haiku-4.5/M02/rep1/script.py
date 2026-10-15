import bpy
import bmesh
from mathutils import Vector
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new mesh and object
mesh = bpy.data.meshes.new("TerrainMesh")
terrain_obj = bpy.data.objects.new("Terrain", mesh)
bpy.context.collection.objects.link(terrain_obj)
bpy.context.view_layer.objects.active = terrain_obj
terrain_obj.select_set(True)

# Create bmesh
bm = bmesh.new()

# Grid dimensions - 100x100 subdivisions
grid_size = 100
scale = 0.5  # Scale of each grid cell

# Create vertices with noise-based heights
vertices = []
for y in range(grid_size + 1):
    for x in range(grid_size + 1):
        # Position in world space
        pos_x = x * scale
        pos_y = y * scale
        
        # Generate height using multiple octaves of Perlin noise
        height = 0
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0
        
        # Multiple octaves for more natural terrain
        for octave in range(4):
            # Use mathutils.noise.noise_vector for Perlin noise
            noise_val = bpy.app.driver_namespace.get('noise', None)
            
            # Simple hash-based noise function as fallback
            seed = int((pos_x * frequency) * 73856093 ^ 
                      (pos_y * frequency) * 19349663)
            seed = (seed ^ (seed >> 13)) * 2654435761
            noise_sample = ((seed & 0x7fffffff) / 2147483647.0) * 2 - 1
            
            height += noise_sample * amplitude
            max_amplitude += amplitude
            
            amplitude *= 0.5
            frequency *= 2.0
        
        height = (height / max_amplitude) * 3.0
        
        # Create vertex
        vert = bm.verts.new((pos_x, pos_y, height))
        vertices.append(vert)

# Create faces from vertices
for y in range(grid_size):
    for x in range(grid_size):
        # Get the four vertices of this quad
        v0 = vertices[y * (grid_size + 1) + x]
        v1 = vertices[y * (grid_size + 1) + (x + 1)]
        v2 = vertices[(y + 1) * (grid_size + 1) + (x + 1)]
        v3 = vertices[(y + 1) * (grid_size + 1) + x]
        
        # Create two triangles for each quad
        try:
            bm.faces.new([v0, v1, v2])
            bm.faces.new([v0, v2, v3])
        except:
            pass

# Update mesh
bm.to_mesh(mesh)
bm.free()

# Update mesh data
mesh.update()

# Apply smooth shading for better appearance
bpy.context.view_layer.objects.active = terrain_obj
bpy.ops.object.shade_smooth()

print(f"Terrain created with {len(mesh.vertices)} vertices and {len(mesh.polygons)} faces")
