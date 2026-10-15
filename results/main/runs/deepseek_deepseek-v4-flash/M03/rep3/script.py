import bpy
import bmesh
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Vaso profile -------------------------------------------------
R_BASE = 0.8
KEY_POINTS = [
    (0.05, 0.8),   # (height, radius)
    (0.10, 0.8),
    (0.50, 1.2),
    (0.90, 0.9),
    (1.30, 0.5),
    (1.60, 0.35),
    (2.00, 0.55),
]

def catmull(p0, p1, p2, p3, t):
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        (2.0 * p1) +
        (-p0 + p2) * t +
        (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 +
        (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
    )

def sample_wall(points, samples_per_segment=5):
    pts = list(points)
    result = [pts[0]]
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        for s in range(1, samples_per_segment + 1):
            t = s / samples_per_segment
            h = catmull(p0[0], p1[0], p2[0], p3[0], t)
            r = catmull(p0[1], p1[1], p2[1], p3[1], t)
            result.append((h, r))
    return result

wall = sample_wall(KEY_POINTS, samples_per_segment=5)

# Profile as (radius, height)
profile = [(0.0, 0.0)]           # centre of the base
profile.append((R_BASE, 0.0))    # outer edge of the base
for h, r in wall:
    profile.append((r, h))

# --- Build lathe mesh --------------------------------------------
M = 64  # segments around the axis

mesh = bpy.data.meshes.new("Vase")
obj = bpy.data.objects.new("Vase", mesh)
bpy.context.scene.collection.objects.link(obj)

bm = bmesh.new()
verts = []

for r, z in profile:
    if r == 0.0:
        v = bm.verts.new((0.0, 0.0, z))
        verts.append([v])
    else:
        ring = []
        for j in range(M):
            theta = 2.0 * math.pi * j / M
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            v = bm.verts.new((x, y, z))
            ring.append(v)
        verts.append(ring)

for i in range(len(profile) - 1):
    r0, _ = profile[i]
    r1, _ = profile[i + 1]

    if r0 == 0.0 and r1 > 0.0:
        # Bottom disk: fan from the centre vertex
        centre = verts[i][0]
        next_ring = verts[i + 1]
        for j in range(M):
            a = next_ring[j]
            b = next_ring[(j + 1) % M]
            bm.faces.new((centre, b, a))

    elif r0 > 0.0 and r1 > 0.0:
        # Ordinary wall quad
        cur_ring = verts[i]
        next_ring = verts[i + 1]
        for j in range(M):
            v00 = cur_ring[j]
            v10 = cur_ring[(j + 1) % M]
            v11 = next_ring[(j + 1) % M]
            v01 = next_ring[j]
            bm.faces.new((v00, v10, v11, v01))

bmesh.ops.recalc_face_normals(bm, inside=False)

# Crease the sharp base edge (ring index 1)
z_crease = profile[1][1]
r_crease = profile[1][0]
for e in bm.edges:
    if len(e.verts) != 2:
        continue
    a, b = e.verts
    if (abs(a.co.z - z_crease) < 1e-6 and abs(a.co.xy.length - r_crease) < 1e-6 and
        abs(b.co.z - z_crease) < 1e-6 and abs(b.co.xy.length - r_crease) < 1e-6):
        e.crease = 1.0

bm.to_mesh(mesh)
bm.free()

# Smooth shading on all polygons
for poly in mesh.polygons:
    poly.use_smooth = True

mesh.update()

# Subdivision Surface modifier
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 2
