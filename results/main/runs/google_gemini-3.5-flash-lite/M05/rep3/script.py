import bpy
import bmesh
import math
import mathutils

# --- Cleanup Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Parameters ---
cols = 10
rows = 10
radius = 1.0          # Outer radius of the hexagon
wall_gap = 0.1        # Gap between adjacent cells
extrusion_height = 2.5

# Hexagon geometry math
# Distance from center to flat side is r * sqrt(3)/2
# For a honeycomb grid, the spacing must account for the gap.
# Let's scale down the individual hexagons to create the gap.
# Effective radius for the outer boundary of a cell:
r_eff = radius - wall_gap * 0.5

dx = r_eff * math.sqrt(3)
dy = r_eff * 1.5

# Create a new mesh and object for the honeycomb
mesh = bpy.data.meshes.new("HoneycombMesh")
obj = bpy.data.object.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Helper function to create a single hexagonal prism bmesh
def create_hex_prism(bm, center_x, center_y, r, height):
    verts = []
    # Create bottom and top loops
    for z_val in (0.0, height):
        loop_verts = []
        for i in range(6):
            angle = math.radians(60 * i + 30) # Pointy topped
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)
            loop_verts.append(bm.verts.new((x, y, z_val)))
        verts.append(loop_verts)
    
    # Bottom face (reversed normal)
    bottom_face_verts = list(reversed(verts[0]))
    bm.faces.new(bottom_face_verts)
    
    # Top face
    top_face_verts = verts[1]
    bm.faces.new(top_face_verts)
    
    # Side faces
    for i in range(6):
            v1 = verts[0][i]
            v2 = verts[0][(i + 1) % 6]
            v3 = verts[1][(i + 1) % 6]
            v4 = verts[1][i]
            bm.faces.new((v1, v2, v3, v4))

# Generate the 10x10 grid with alternating row offsets
for r_idx in range(rows):
    # Offset every second row
    row_offset = (dx / 2.0) if (r_idx % 2 == 1) else 0.0
    y_pos = r_idx * dy
    
    for c_idx in range(cols):
        x_pos = c_idx * dx + row_offset
        create_hex_prism(bm, x_pos, y_pos, r_eff, extrusion_height)

# Finalize mesh
bm.to_mesh(mesh)
bm.free()

# Optional: Center the origin of the geometry
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Shade smooth for clean look
for f in mesh.polygons:
    f.use_smooth = True
