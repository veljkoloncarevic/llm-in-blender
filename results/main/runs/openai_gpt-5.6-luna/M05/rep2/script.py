import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
rows = 10
cols = 10
cell_radius = 0.47
grid_radius = 0.50
cell_depth = 0.28
gap = 0.03

# Pointy-top hexagon grid spacing
x_spacing = 1.5 * grid_radius
y_spacing = math.sqrt(3.0) * grid_radius

vertices = []
faces = []

# Center the staggered grid around the origin
row_y_values = [
    (row - (rows - 1) / 2.0) * y_spacing
    for row in range(rows)
]

for row in range(rows):
    # Alternate row offset, producing a correctly staggered honeycomb layout
    row_offset = 0.5 * x_spacing if row % 2 else 0.0

    for col in range(cols):
        cx = (col - (cols - 1) / 2.0) * x_spacing + row_offset
        cy = row_y_values[row]

        base_index = len(vertices)

        # Bottom ring
        for i in range(6):
            angle = math.radians(i * 60.0)
            vertices.append((
                cx + cell_radius * math.cos(angle),
                cy + cell_radius * math.sin(angle),
                -cell_depth / 2.0
            ))

        # Top ring
        for i in range(6):
            angle = math.radians(i * 60.0)
            vertices.append((
                cx + cell_radius * math.cos(angle),
                cy + cell_radius * math.sin(angle),
                cell_depth / 2.0
            ))

        # Bottom cap, reversed for outward-facing normals
        faces.append(tuple(base_index + i for i in reversed(range(6))))

        # Top cap
        faces.append(tuple(base_index + 6 + i for i in range(6)))

        # Six side faces
        for i in range(6):
            j = (i + 1) % 6
            faces.append((
                base_index + i,
                base_index + j,
                base_index + 6 + j,
                base_index + 6 + i
            ))

# Create the mesh and object
mesh = bpy.data.meshes.new("HoneycombPanelMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

panel = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(panel)

# Assign a warm honey-colored material
material = bpy.data.materials.new("HoneycombHoney")
material.diffuse_color = (0.9, 0.42, 0.06, 1.0)
material.metallic = 0.0
material.roughness = 0.38
panel.data.materials.append(material)

# Ensure flat, crisp prism faces
for polygon in mesh.polygons:
    polygon.use_smooth = False

# Make the generated panel the active selection
bpy.context.view_layer.objects.active = panel
panel.select_set(True)
