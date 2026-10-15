import bpy
import bmesh
import math

# Remove all existing objects
if bpy.context.active_object:
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
teeth = 24
thickness = 0.3
outer_radius = 1.0
root_radius = 0.75
hole_radius = 0.4
tip_segments = 4
root_segments = 4

# Create gear profile (2D outer contour) and inner hole contour
bm = bmesh.new()
T = 2 * math.pi / teeth
alpha = T * 0.2
beta = T * 0.35

outer_pts = []
def add_outer(angle, radius):
    outer_pts.append((radius * math.cos(angle), radius * math.sin(angle), 0.0))

# Outer contour, starting at root before first tooth
add_outer(-beta, root_radius)
for i in range(teeth):
    theta = i * T
    # Flank up
    add_outer(theta - alpha, outer_radius)
    # Tip arc
    for s in range(1, tip_segments + 1):
        ang = theta - alpha + (2 * alpha) * s / tip_segments
        add_outer(ang, outer_radius)
    # Flank down
    add_outer(theta + beta, root_radius)

    # Root gap to next tooth
    if i < teeth - 1:
        next_theta = (i + 1) * T
        gap_start = theta + beta
        gap_end = next_theta - beta
        gap_span = gap_end - gap_start
        for s in range(1, root_segments + 1):
            ang = gap_start + gap_span * s / root_segments
            add_outer(ang, root_radius)
    else:
        # Final root gap closes back to the start
        gap_start = theta + beta
        gap_end = 2 * math.pi - beta
        gap_span = gap_end - gap_start
        for s in range(1, root_segments):
            ang = gap_start + gap_span * s / root_segments
            add_outer(ang, root_radius)

N = len(outer_pts)

# Inner contour: evenly distributed circle with same vertex count
inner_pts = []
for i in range(N):
    ang = -beta + (2 * math.pi * i / N)
    inner_pts.append((hole_radius * math.cos(ang), hole_radius * math.sin(ang), 0.0))

# Build vertices
h = thickness / 2.0
out_top = []
out_bot = []
in_top = []
in_bot = []

for x, y, _ in outer_pts:
    out_top.append(bm.verts.new((x, y, h)))
    out_bot.append(bm.verts.new((x, y, -h)))
for x, y, _ in inner_pts:
    in_top.append(bm.verts.new((x, y, h)))
    in_bot.append(bm.verts.new((x, y, -h)))

# Build quads
for i in range(N):
    ni = (i + 1) % N
    # Top ring
    bm.faces.new((out_top[i], out_top[ni], in_top[ni], in_top[i]))
    # Bottom ring
    bm.faces.new((in_bot[i], in_bot[ni], out_bot[ni], out_bot[i]))
    # Outer side wall
    bm.faces.new((out_bot[i], out_bot[ni], out_top[ni], out_top[i]))
    # Inner side wall (hole)
    bm.faces.new((in_bot[i], in_top[i], in_top[ni], in_bot[ni]))

# Recalculate normals so they point outward
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
bm.normal_update()

# Create mesh object
mesh = bpy.data.meshes.new("SpurGear")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.scene.collection.objects.link(obj)
