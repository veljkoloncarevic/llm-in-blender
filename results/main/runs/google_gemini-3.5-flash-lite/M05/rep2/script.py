import bpy
import bmesh
import math
from mathutils import Matrix

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Parameters for honeycomb
rows = 10
cols = 10
radius = 1.0          # Outer radius of the hexagon
wall_gap = 0.1        # Gap between cells (scaled down slightly for separation)
height = 2.0          # Height of the hexagonal prisms

# Geometry calculations for pointy-topped hexagons
# Width and height of pointy-topped hex bounding box
hex_w = math.sqrt(3) * radius
hex_h = 2.0 * radius

# Spacing offsets for interlocking pointy-topped hex grid
dx = hex_w + wall_gap
dy = 0.75 * hex_h + wall_gap * 0.5

# 3. Use BMesh to build all cells in a single mesh for efficiency and clean topology
bm = bmesh.new()

def create_hex_prism(matrix, r, h):
    """Creates a single hexagonal prism at the given transformation matrix."""
    # Create top and bottom faces by extruding a base circle/gon
    verts = []
    for i in range(6):
        angle = i * (2 * math.pi / 6) + math.pi / 6  # Pointy-topped rotation
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        verts.append(bm.verts.new((x, y, 0)))
    
    face = bm.faces.new(verts)
    
    # Extrude up to create height
    extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
    
    # Find translated vertices and move them up
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=translate_verts, vec=(0, 0, h))
    
    # Apply the grid position matrix
    all_prism_verts = list(face.verts) + translate_verts
    bmesh.ops.transform(bm, matrix=matrix, verts=all_prism_verts)

# 4. Generate the 10x10 grid with alternating row offsets
for r in range(rows):
    # Offset every second row horizontally
    row_offset = (hex_w / 2.0) if (r % 2 == 1) else 0.0
    
    for c in range(cols):
        # Calculate center position for this cell
        x = c * dx + row_offset
        y = r * dy
        z = 0.0
        
        # Build transform matrix for the cell
        mat = Matrix.Translation((x, y, z))
        
        # Slightly scale down individual cells to guarantee gaps even with the gap offset
        cell_scale = (radius - wall_gap * 0.5) / radius
        mat = mat @ Matrix.Scale(cell_scale, 4, (1, 1, 0))
        
        create_hex_prism(mat, radius, height)

# 5. Clean up BMesh data (remove internal overlapping faces if desired, 
# but gaps make them separate entities, so just ensure normals are consistent)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# 6. Create mesh and object from BMesh
mesh = bpy.data.meshes.new("HoneycombPanelMesh")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(obj)

# Set to smooth shading for a clean look
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Select the object
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
