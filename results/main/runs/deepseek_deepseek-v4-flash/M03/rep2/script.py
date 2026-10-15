import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Control points (height, radius) for the vase profile
control_points = [
    (0.0, 0.7),
    (0.1, 0.7),
    (0.25, 1.0),
    (0.45, 1.3),
    (0.65, 1.0),
    (0.8, 0.35),
    (1.0, 0.4),
    (1.2, 0.4),
]
ctl = [Vector((z, r)) for z, r in control_points]

# Catmull-Rom interpolation for a smooth profile
def catmull_rom(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        (2.0 * p1) +
        (-p0 + p2) * t +
        (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 +
        (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
    )

segments = 64          # radial resolution
profile_steps = 40     # vertical resolution
z_min = ctl[0].x
z_max = ctl[-1].x

# Generate profile points
profile = []
for i in range(profile_steps):
    z = z_min + (z_max - z_min) * i / (profile_steps - 1)

    idx = 0
    for k in range(len(ctl) - 1):
        if ctl[k].x <= z <= ctl[k + 1].x:
            idx = k
            break
    if z >= ctl[-1].x:
        idx = len(ctl) - 2

    p0 = ctl[max(0, idx - 1)]
    p1 = ctl[idx]
    p2 = ctl[idx + 1]
    p3 = ctl[min(len(ctl) - 1, idx + 2)]

    denom = p2.x - p1.x
    t = (z - p1.x) / denom if denom != 0.0 else 0.0
    pt = catmull_rom(p0, p1, p2, p3, t)
    r = max(0.05, pt.y)
    profile.append((pt.x, r))

# Build the lathe mesh
bm = bmesh.new()

# Body vertices
for z, r in profile:
    for j in range(segments):
        theta = 2.0 * math.pi * j / segments
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        bm.verts.new((x, y, z))

# Center vertex for the flat base
center = bm.verts.new((0.0, 0.0, profile[0][0]))

# Side faces (quads)
for i in range(profile_steps - 1):
    for j in range(segments):
        j1 = (j + 1) % segments
        v_bottom_j1 = bm.verts[i * segments + j1]
        v_top_j1 = bm.verts[(i + 1) * segments + j1]
        v_top_j = bm.verts[(i + 1) * segments + j]
        v_bottom_j = bm.verts[i * segments + j]
        face = bm.faces.new((v_bottom_j1, v_top_j1, v_top_j, v_bottom_j))
        face.smooth = True

# Base cap (triangles, downward facing)
for j in range(segments):
    j1 = (j + 1) % segments
    v_j = bm.verts[j]
    v_j1 = bm.verts[j1]
    face = bm.faces.new((center, v_j1, v_j))
    face.smooth = True

# Create mesh object
mesh = bpy.data.meshes.new("Vase")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(obj)

# Set smooth shading on all polygons
for poly in mesh.polygons:
    poly.use_smooth = True

# Add Subdivision Surface modifier
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 2
mod.subdivision_type = 'CATMULL_CLARK'
