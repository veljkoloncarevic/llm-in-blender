import bpy
import bmesh
import math
from mathutils import Vector

# Ensure object mode
if bpy.ops.object.mode_set.poll():
    bpy.ops.object.mode_set(mode='OBJECT')

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Profile control points as (radius, height)
P = [
    (0.0, 0.0),   # base center
    (1.8, 0.0),   # base edge
    (2.0, 0.5),   # foot
    (2.6, 1.5),   # lower body
    (4.0, 3.5),   # body
    (4.2, 5.5),   # widest point
    (3.0, 7.5),   # shoulder
    (1.6, 9.2),   # neck
    (1.2, 10.2),  # neck opening
    (1.5, 10.8),  # lip
]

# Generate profile points by linear interpolation
sub_steps = 8   # subdivisions per control segment
pts = []
for i in range(len(P) - 1):
    p0 = Vector(P[i])
    p1 = Vector(P[i + 1])
    for j in range(sub_steps):
        t = j / sub_steps
        pts.append(p0.lerp(p1, t))
pts.append(Vector(P[-1]))

# Number of rotational segments
N = 32

# Create the lathe mesh
bm = bmesh.new()
row_verts = []

for r, z in pts:
    if abs(r) < 1e-6:
        v = bm.verts.new((0.0, 0.0, z))
        row_verts.append([v])
    else:
        row = []
        for i in range(N):
            ang = 2.0 * math.pi * i / N
            v = bm.verts.new((r * math.cos(ang), r * math.sin(ang), z))
            row.append(v)
        row_verts.append(row)

# Create faces between consecutive profile rows
for j in range(len(pts) - 1):
    r0 = pts[j][0]
    r1 = pts[j + 1][0]
    row0 = row_verts[j]
    row1 = row_verts[j + 1]

    if abs(r0) < 1e-6:
        # Triangle fan from centre to first ring
        centre = row0[0]
        for i in range(N):
            v1 = row1[i]
            v2 = row1[(i + 1) % N]
            bm.faces.new((centre, v1, v2))
    else:
        # Quads between two ring rows
        for i in range(N):
            a = row0[i]
            b = row0[(i + 1) % N]
            c = row1[(i + 1) % N]
            d = row1[i]
            bm.faces.new((a, b, c, d))

# Crease the outer edge of the flat base
bm.edges.ensure_lookup_table()
base_idx = sub_steps  # profile point at P[1]
if base_idx < len(row_verts):
    base_ring = row_verts[base_idx]
    base_set = set(base_ring)
    for edge in bm.edges:
        v0 = edge.verts[0]
        v1 = edge.verts[1]
        if v0 in base_set and v1 in base_set:
            edge.crease = 1.0

# Create mesh object
mesh = bpy.data.meshes.new("Vase")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(obj)

# Smooth shading
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()

# Add Subdivision Surface modifier
mod = obj.modifiers.new(name="Subdivision Surface", type='SUBSURF')
mod.levels = 2
mod.render_levels = 2
