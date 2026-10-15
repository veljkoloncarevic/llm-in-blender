import bpy
import math

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Honeycomb dimensions
rows = 10
cols = 10
radius = 0.5
cell_depth = 0.3

# Pitches are slightly larger than the touching-cell layout, creating gaps
horizontal_pitch = radius * 1.58
vertical_pitch = radius * math.sqrt(3.0) * 1.06

vertices = []
faces = []

z_bottom = -cell_depth / 2.0
z_top = cell_depth / 2.0

for row in range(rows):
    # Center the entire staggered panel while offsetting alternating rows
    row_offset = (0.5 if row % 2 else 0.0) * horizontal_pitch
    row_offset -= horizontal_pitch * 0.25

    y = (row - (rows - 1) / 2.0) * vertical_pitch

    for col in range(cols):
        x = (col - (cols - 1) / 2.0) * horizontal_pitch + row_offset

        start = len(vertices)

        # Pointy-top regular hexagon
        for i in range(6):
            angle = math.radians(i * 60.0)
            vertices.append((
                x + radius * math.cos(angle),
                y + radius * math.sin(angle),
                z_bottom
            ))

        for i in range(6):
            angle = math.radians(i * 60.0)
            vertices.append((
                x + radius * math.cos(angle),
                y + radius * math.sin(angle),
                z_top
            ))

        # Bottom and top faces
        faces.append(tuple(start + i for i in reversed(range(6))))
        faces.append(tuple(start + 6 + i for i in range(6)))

        # Six side faces
        for i in range(6):
            j = (i + 1) % 6
            faces.append((
                start + i,
                start + j,
                start + 6 + j,
                start + 6 + i
            ))

mesh = bpy.data.meshes.new("HoneycombPanelMesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

panel = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(panel)

# Create a warm honey-colored material
material = bpy.data.materials.new("HoneycombMaterial")
material.diffuse_color = (0.95, 0.48, 0.08, 1.0)
material.metallic = 0.0
material.roughness = 0.38
panel.data.materials.append(material)

# Useful metadata
panel["rows"] = rows
panel["columns"] = cols
panel["cell_count"] = rows * cols
panel["face_count"] = len(faces)
