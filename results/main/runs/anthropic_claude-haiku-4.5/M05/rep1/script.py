import bpy
import bmesh
from mathutils import Vector
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
grid_size = 10  # 10x10 grid
hex_radius = 0.4  # Circumradius of hexagon
gap = 0.05  # Gap between cells
height = 0.3  # Height of hexagonal prism

# Create a single hexagonal prism
def create_hex_prism(center, radius, height):
    """Create a hexagonal prism mesh"""
    verts = []
    faces = []
    
    # Bottom hexagon vertices
    for i in range(6):
        angle = i * math.pi / 3
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        z = center.z
        verts.append((x, y, z))
    
    # Top hexagon vertices
    for i in range(6):
        angle = i * math.pi / 3
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        z = center.z + height
        verts.append((x, y, z))
    
    # Bottom face
    faces.append(tuple(range(6)))
    
    # Top face
    faces.append(tuple(range(6, 12)))
    
    # Side faces
    for i in range(6):
        next_i = (i + 1) % 6
        faces.append((i, next_i, next_i + 6, i + 6))
    
    return verts, faces

# Create mesh and object
mesh = bpy.data.meshes.new("HoneycombPanel")
obj = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Use bmesh to build the honeycomb
bm = bmesh.new()

# Calculate spacing between hexagon centers
# For a regular hexagon with circumradius r, the width is 2r
# Horizontal spacing between adjacent hex centers
hex_width = 2 * hex_radius
# Vertical spacing (distance between rows)
hex_height = hex_radius * math.sqrt(3)

# Account for gaps
spacing_x = hex_width + gap
spacing_y = hex_height + gap

# Generate hexagonal prisms in a 10x10 grid with alternating row offset
for row in range(grid_size):
    for col in range(grid_size):
        # Calculate position with alternating row offset
        x = col * spacing_x
        # Offset every other row by half the horizontal spacing
        if row % 2 == 1:
            x += spacing_x / 2
        y = row * spacing_y
        z = 0
        
        center = Vector((x, y, z))
        verts, faces = create_hex_prism(center, hex_radius, height)
        
        # Add vertices to bmesh
        vert_indices = [bm.verts.new(v) for v in verts]
        
        # Add faces to bmesh
        for face in faces:
            try:
                face_verts = [vert_indices[i] for i in face]
                bm.faces.new(face_verts)
            except:
                pass

# Update mesh from bmesh
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Apply smooth shading for better appearance
bpy.context.view_layer.objects.active = obj
bpy.ops.object.shade_smooth()

# Center the object
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
