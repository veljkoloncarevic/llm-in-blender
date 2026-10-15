import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
rows = 10
cols = 10
radius = 1.0
height = 0.4
gap = 0.12

# Flat-top hexagon spacing with staggered alternating rows
hex_width = math.sqrt(3.0) * radius
column_spacing = hex_width + gap
row_spacing = 1.5 * radius + gap

vertices = []
faces = []

# Hexagon angles for flat-top orientation
angles = [math.radians(30.0 + i * 60.0) for i in range(6)]

# Center the overall panel approximately around the origin
panel_width = (cols - 1) * column_spacing + hex_width + column_spacing * 0.5
panel_height = (rows - 1) * row_spacing + 2.0 * radius
x_origin = -panel_width * 0.5
y_origin = -panel_height * 0.5

for row in range(rows):
    row_offset = 0.5 * column_spacing if row % 2 else 0.0

    for col in range(cols):
        cx = x_origin + radius * math.sqrt(3.0) * 0.5 + col * column_spacing + row_offset
        cy = y_origin + radius + row * row_spacing

        base_index = len(vertices)

        # Bottom and top rings
        for z in (0.0, height):
            for angle in angles:
                vertices.append((
                    cx + radius * math.cos(angle),
                    cy + radius * math.sin(angle),
                    z
                ))

        # Bottom face, top face, and six side faces
        faces.append(tuple(base_index + i for i in reversed(range(6))))
        faces.append(tuple(base_index + 6 + i for i in range(6)))

        for i in range(6):
            ni = (i + 1) % 6
            faces.append((
                base_index + i,
                base_index + ni,
                base_index + 6 + ni,
                base_index + 6 + i
            ))

# Create one mesh containing all 100 disconnected hexagonal prisms
mesh = bpy.data.meshes.new("HoneycombPanelMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

panel = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(panel)

# Assign a warm honey-colored material
material = bpy.data.materials.new("HoneycombMaterial")
material.diffuse_color = (0.8, 0.32, 0.04, 1.0)
material.metallic = 0.0
material.roughness = 0.42
panel.data.materials.append(material)

# Select the generated panel
bpy.context.view_layer.objects.active = panel
panel.select_set(True)
