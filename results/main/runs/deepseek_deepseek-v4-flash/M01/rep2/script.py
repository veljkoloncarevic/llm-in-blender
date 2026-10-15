import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.context.scene.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Parameters
num_steps = 24
angle_step = math.radians(15)      # 15 degrees per step
height_step = 0.2                  # rise per step
total_rise = num_steps * height_step
total_angle = 2 * math.pi          # 24 * 15° = 360°
inner_radius = 0.4                 # central column radius
outer_radius = 2.0                 # outer edge of steps / handrail radius

bm = bmesh.new()

# --- Steps ---
for i in range(num_steps):
    a0 = i * angle_step
    a1 = a0 + angle_step
    z0 = i * height_step
    z1 = (i + 1) * height_step

    b0 = bm.verts.new((inner_radius * math.cos(a0), inner_radius * math.sin(a0), z0))
    b1 = bm.verts.new((outer_radius * math.cos(a0), outer_radius * math.sin(a0), z0))
    b2 = bm.verts.new((outer_radius * math.cos(a1), outer_radius * math.sin(a1), z0))
    b3 = bm.verts.new((inner_radius * math.cos(a1), inner_radius * math.sin(a1), z0))
    t0 = bm.verts.new((inner_radius * math.cos(a0), inner_radius * math.sin(a0), z1))
    t1 = bm.verts.new((outer_radius * math.cos(a0), outer_radius * math.sin(a0), z1))
    t2 = bm.verts.new((outer_radius * math.cos(a1), outer_radius * math.sin(a1), z1))
    t3 = bm.verts.new((inner_radius * math.cos(a1), inner_radius * math.sin(a1), z1))

    bm.faces.new((b0, b3, b2, b1))      # bottom
    bm.faces.new((t0, t1, t2, t3))      # top
    bm.faces.new((b0, b1, t1, t0))      # start radial face
    bm.faces.new((b3, b2, t2, t3))      # end radial face
    bm.faces.new((b0, b3, t3, t0))      # inner side
    bm.faces.new((b1, b2, t2, t1))      # outer side

# --- Central cylindrical column ---
column_segments = 32
bottom_verts = []
top_verts = []
for i in range(column_segments):
    a = 2 * math.pi * i / column_segments
    bottom_verts.append(bm.verts.new((inner_radius * math.cos(a), inner_radius * math.sin(a), 0)))
    top_verts.append(bm.verts.new((inner_radius * math.cos(a), inner_radius * math.sin(a), total_rise)))

bm.faces.new(bottom_verts)
bm.faces.new(top_verts)

for i in range(column_segments):
    j = (i + 1) % column_segments
    bm.faces.new((bottom_verts[i], bottom_verts[j], top_verts[j], top_verts[i]))

# --- Helical handrail along the outer edge ---
rail_radius = outer_radius
rail_base_height = 1.0
tube_radius = 0.05
circle_segments = 8
path_segments = 180

dz = total_rise / total_angle  # vertical rate per radian

centers = []
circles = []
for i in range(path_segments + 1):
    theta = i * (total_angle / path_segments)
    z = rail_base_height + theta * dz
    center = Vector((rail_radius * math.cos(theta), rail_radius * math.sin(theta), z))
    centers.append(center)

    T = Vector((-rail_radius * math.sin(theta), rail_radius * math.cos(theta), dz)).normalized()
    N = Vector((math.cos(theta), math.sin(theta), 0.0))
    B = T.cross(N).normalized()

    circle_verts = []
    for j in range(circle_segments):
        u = 2 * math.pi * j / circle_segments
        offset = tube_radius * (math.cos(u) * N + math.sin(u) * B)
        circle_verts.append(bm.verts.new(center + offset))
    circles.append(circle_verts)

# Side quads of the handrail tube
for i in range(path_segments):
    for j in range(circle_segments):
        j2 = (j + 1) % circle_segments
        v0 = circles[i][j]
        v1 = circles[i][j2]
        v2 = circles[i + 1][j2]
        v3 = circles[i + 1][j]
        bm.faces.new((v0, v1, v2, v3))

# End caps
for circle, center in ((circles[0], centers[0]), (circles[-1], centers[-1])):
    center_v = bm.verts.new(center)
    for j in range(circle_segments):
        j2 = (j + 1) % circle_segments
        bm.faces.new((circle[j], circle[j2], center_v))

# Finalize mesh
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
mesh = bpy.data.meshes.new("SpiralStaircase")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("SpiralStaircase", mesh)
bpy.context.scene.collection.objects.link(obj)
