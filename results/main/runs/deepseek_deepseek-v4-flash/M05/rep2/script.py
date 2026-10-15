import bpy
import math

# Ensure we are in object mode before clearing
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters
rows = 10
cols = 10
base_radius = 1.0
gap_factor = 0.9
cell_radius = base_radius * gap_factor
height = 0.5

# Lattice constants for pointy-top hexagons
col_spacing_x = math.sqrt(3) * base_radius
row_spacing_y = 1.5 * base_radius

vertices = []
faces = []

for r in range(rows):
    x_offset = col_spacing_x / 2.0 if r % 2 else 0.0
    for c in range(cols):
        cx = c * col_spacing_x + x_offset
        cy = r * row_spacing_y

        base_idx = len(vertices)

        # Bottom vertices (z = 0)
        for i in range(6):
            angle = math.radians(30 + 60 * i)
            vertices.append((cx + cell_radius * math.cos(angle),
                             cy + cell_radius * math.sin(angle),
                             0.0))

        # Top vertices (z = height)
        for i in range(6):
            angle = math.radians(30 + 60 * i)
            vertices.append((cx + cell_radius * math.cos(angle),
                             cy + cell_radius * math.sin(angle),
                             height))

        b0 = base_idx
        t0 = base_idx + 6

        # Bottom face (normal -Z)
        faces.append([b0 + 5, b0 + 4, b0 + 3, b0 + 2, b0 + 1, b0])
        # Top face (normal +Z)
        faces.append([t0 + 0, t0 + 1, t0 + 2, t0 + 3, t0 + 4, t0 + 5])

        # Side faces
        for i in range(6):
            i_next = (i + 1) % 6
            faces.append([b0 + i, b0 + i_next, t0 + i_next, t0 + i])

# Create mesh and object
mesh = bpy.data.meshes.new("HoneycombPanel")
mesh.from_pydata(vertices, [], faces)
mesh.update()

obj = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(obj)
