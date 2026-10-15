import bpy
import bmesh
import math
from mathutils import Vector

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
grid_width = 10
grid_height = 10
hex_radius = 0.4  # Circumradius of hexagon
hex_height = 0.5  # Height of prism
gap = 0.02  # Gap between cells

# Create a single hexagonal prism
def create_hex_prism(radius, height):
    """Create a hexagonal prism mesh"""
    mesh = bpy.data.meshes.new("HexPrism")
    bm = bmesh.new()
    
    # Create vertices for top and bottom hexagons
    vertices_top = []
    vertices_bottom = []
    
    for i in range(6):
        angle = i * math.pi / 3  # 60 degrees
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        # Top hexagon
        v_top = bm.verts.new((x, y, height / 2))
        vertices_top.append(v_top)
        
        # Bottom hexagon
        v_bottom = bm.verts.new((x, y, -height / 2))
        vertices_bottom.append(v_bottom)
    
    # Create top face
    bm.faces.new(vertices_top)
    
    # Create bottom face (reversed for correct normal)
    bm.faces.new(vertices_bottom[::-1])
    
    # Create side faces
    for i in range(6):
        next_i = (i + 1) % 6
        face_verts = [
            vertices_bottom[i],
            vertices_bottom[next_i],
            vertices_top[next_i],
            vertices_top[i]
        ]
        bm.faces.new(face_verts)
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return mesh

# Create the honeycomb grid
hex_mesh = create_hex_prism(hex_radius, hex_height)

# Calculate spacing between hexagon centers
# For a regular hexagon with circumradius r, width is 2*r and height is sqrt(3)*r
hex_width = 2 * hex_radius
hex_height_spacing = math.sqrt(3) * hex_radius

# Spacing with gaps
spacing_x = hex_width + gap
spacing_y = hex_height_spacing + gap

# Create instances in grid
for row in range(grid_height):
    for col in range(grid_width):
        # Calculate position with alternating row offset
        x = col * spacing_x
        y = row * spacing_y
        
        # Offset every other row by half the x-spacing (standard honeycomb pattern)
        if row % 2 == 1:
            x += spacing_x / 2
        
        # Create object
        obj = bpy.data.objects.new(f"Hexagon_{row}_{col}", hex_mesh)
        bpy.context.collection.objects.link(obj)
        
        # Set location
        obj.location = (x, y, 0)

# Clean up the base mesh if not used by any object
if hex_mesh.users == 0:
    bpy.data.meshes.remove(hex_mesh)

# Select all honeycomb objects and apply transforms
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

print(f"Honeycomb panel created: {grid_width} x {grid_height} hexagonal prisms")
print(f"Total objects: {grid_width * grid_height}")
print(f"Faces per prism: 8 (2 hexagons + 6 rectangles)")
print(f"Total face count: {grid_width * grid_height * 8}")
