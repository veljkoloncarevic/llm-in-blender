import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Honeycomb parameters
rows, cols = 10, 10
hex_radius = 1.0          # outer radius of each hexagon
shrink = 0.9              # leaves a small gap between cells
height = 0.5              # prism height

# Pointy-top hexagon geometry
dx = math.sqrt(3.0) * hex_radius
dy = 1.5 * hex_radius
row_offset = dx * 0.5

# Angles for a pointy-top hexagon (degrees)
angles = [math.radians(a) for a in (30, 90, 150, 210, 270, 330)]

# Create mesh and object
mesh = bpy.data.meshes.new("HoneycombPanel")
obj = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.scene.collection.objects.link(obj)

bm = bmesh.new()

for row in range(rows):
    y_pos = row * dy
    x_off = row_offset if (row % 2) else 0.0

    for col in range(cols):
        cx = col * dx + x_off
        center = Vector((cx, y_pos, 0.0))

        bottom_verts = []
        top_verts = []

        for ang in angles:
            vx = math.cos(ang) * hex_radius * shrink
            vy = math.sin(ang) * hex_radius * shrink
            v = Vector((vx, vy, 0.0))

            bottom_verts.append(bm.verts.new(center + v))
            top_verts.append(bm.verts.new(center + v + Vector((0.0, 0.0, height))))

        # Bottom face (reverse order → normal points down)
        bm.faces.new(list(reversed(bottom_verts)))

        # Top face (normal points up)
        bm.faces.new(top_verts)

        # Side faces
        for i in range(6):
            bv0 = bottom_verts[i]
            bv1 = bottom_verts[(i + 1) % 6]
            tv1 = top_verts[(i + 1) % 6]
            tv0 = top_verts[i]
            bm.faces.new((bv0, bv1, tv1, tv0))

bm.to_mesh(mesh)
bm.free()
