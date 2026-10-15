import bpy
import bmesh
from mathutils import Vector
import math

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
grid_width = 10
grid_height = 10
hex_radius = 0.45  # Circumradius of hexagon
gap = 0.08  # Gap between cells
height = 0.3  # Height of prism

# Create a single hexagonal prism
def create_hexagon_prism(center, hex_radius, height):
    """Create a hexagonal prism at the given center position"""
    mesh = bpy.data.meshes.new("hex_prism")
    obj = bpy.data.objects.new("hex_prism", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # Create vertices for top and bottom hexagons
    vertices = []
    for i in range(6):
        angle = i * math.pi / 3
        x = center.x + hex_radius * math.cos(angle)
        y = center.y + hex_radius * math.sin(angle)
        
        # Bottom vertices
        v_bottom = bm.verts.new((x, y, center.z - height / 2))
        vertices.append(v_bottom)
        
        # Top vertices
        v_top = bm.verts.new((x, y, center.z + height / 2))
        vertices.append(v_top)
    
    # Create faces
    # Bottom face
    bottom_verts = [vertices[i*2] for i in range(6)]
    bm.faces.new(bottom_verts)
    
    # Top face
    top_verts = [vertices[i*2 + 1] for i in range(6)]
    bm.faces.new(top_verts)
    
    # Side faces
    for i in range(6):
        next_i = (i + 1) % 6
        v1 = vertices[i * 2]
        v2 = vertices[i * 2 + 1]
        v3 = vertices[next_i * 2 + 1]
        v4 = vertices[next_i * 2]
        bm.faces.new([v1, v4, v3, v2])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj

# Calculate the spacing between hexagon centers
# For a regular hexagon with circumradius r, the width (flat to flat) is sqrt(3)*r
hex_width = math.sqrt(3) * hex_radius
hex_height_vert = 2 * hex_radius

# Spacing with gaps
spacing_x = hex_width + gap
spacing_y = hex_height_vert * 0.75 + gap  # 0.75 accounts for hexagon row offset

# Create honeycomb grid
honeycomb_objects = []
for row in range(grid_height):
    for col in range(grid_width):
        # Offset alternating rows
        x_offset = spacing_x * 0.5 if row % 2 == 1 else 0
        x = col * spacing_x + x_offset
        y = row * spacing_y
        z = 0
        
        center = Vector((x, y, z))
        hex_obj = create_hexagon_prism(center, hex_radius, height)
        honeycomb_objects.append(hex_obj)

# Join all objects into a single mesh
if honeycomb_objects:
    ctx = bpy.context.copy()
    ctx['object'] = honeycomb_objects[0]
    ctx['selected_objects'] = honeycomb_objects
    bpy.ops.object.join(ctx)
    
    # Smooth the result
    final_obj = honeycomb_objects[0]
    final_obj.name = "Honeycomb_Panel"
