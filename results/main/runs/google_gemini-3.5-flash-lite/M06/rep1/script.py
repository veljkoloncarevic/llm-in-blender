import bpy
import bmesh
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the spur gear
num_teeth = 24
thickness = 0.3
module = 0.4
pitch_radius = (num_teeth * module) / 2.0  # 4.8
addendum = module * 1.0  # 0.4
dedendum = module * 1.25  # 0.5
outer_radius = pitch_radius + addendum  # 5.2
root_radius = pitch_radius - dedendum  # 4.3
hole_radius = 1.5

# Resolution parameters
# 4 vertices per tooth: root-start, flank-in, flank-out, root-end
radial_segments = num_teeth * 4
hole_segments = 32

# Create mesh and bmesh
mesh = bpy.data.meshes.new("SpurGear_Mesh")
obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Generate profile vertices
outer_verts = []
inner_verts = []

# Hole vertices (inner circle)
for i in range(hole_segments):
    angle = 2.0 * math.pi * i / hole_segments
    x = math.cos(angle) * hole_radius
    y = math.sin(angle) * hole_radius
    v = bm.verts.new((x, y, -thickness / 2.0))
    inner_verts.append(v)

# Gear profile vertices (outer circle with teeth)
for t in range(num_teeth):
    base_angle = 2.0 * math.pi * t / num_teeth

    # Tooth sub-angles
    da = 2.0 * math.pi / num_teeth

    # 4 points per tooth:
    # 0: Root start
    # 1: Tip start (involute approximation)
    # 2: Tip end
    # 3: Root end
    angles = [
        base_angle - da * 0.35,
        base_angle - da * 0.12,
        base_angle + da * 0.12,
        base_angle + da * 0.35,
    ]

    radii = [root_radius, outer_radius, outer_radius, root_radius]

    for a, r in zip(angles, radii):
        x = math.cos(a) * r
        y = math.sin(a) * r
        v = bm.verts.new((x, y, -thickness / 2.0))
        outer_verts.append(v)

bm.verts.ensure_lookup_table()

# Create bottom cap (N-gon with hole)
# BMesh bridge loops or createface can handle holes if properly ordered,
# but safely building as triangle/quad strips or using BMesh operations is robust.
# Let's use bmesh operations to bridge inner and outer bottom rings, then extrude.

# Actually, an easier procedural way in BMesh:
# 1. Create bottom face (outer profile - hole profile)
# 2. Extrude along Z
# 3. Create top face automatically or via extrusion

# Clear the verts we just made and use a clean bmesh construction
bm.clear()

# Re-build using bmesh create face with hole or bridge
bottom_inner = []
for i in range(hole_segments):
    angle = 2.0 * math.pi * i / hole_segments
    bottom_inner.append(bm.verts.new((math.cos(angle) * hole_radius, math.sin(angle) * hole_radius, -thickness / 2.0)))

bottom_outer = []
for t in range(num_teeth):
    base_angle = 2.0 * math.pi * t / num_teeth
    da = 2.0 * math.pi / num_teeth
    angles = [
        base_angle - da * 0.35,
        base_angle - da * 0.12,
        base_angle + da * 0.12,
        base_angle + da * 0.35,
    ]
    radii = [root_radius, outer_radius, outer_radius, root_radius]
    for a, r in zip(angles, radii):
        bottom_outer.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, -thickness / 2.0)))

bm.verts.ensure_lookup_table()

# Create bottom cap face with a hole
# In BMesh, to make a face with a hole, we can create the outer wire and inner wire,
# but `bmesh.ops.holes_fill` or simply triangulating/bridging is safer.
# Alternative safe method: Build quads between inner circle and outer gear profile.
# Since hole_segments (32) != radial_segments (96), direct bridging is messy.
# Instead, let's fill the gear profile as a fan or N-gon, then cut the center hole using bmesh ops,
# OR build the gear via extrusion of a 2D profile.

bm.clear()

# --- Method: Build 2D profile face, then extrude ---
# 1. Outer profile verts (bottom)
prof_verts = []
total_outer = num_teeth * 4
for i in range(total_outer):
    t = i / 4
    base_angle = 2.0 * math.pi * (t // 1) / num_teeth
    sub = i % 4
    da = 2.0 * math.pi / num_teeth

    # offsets for the 4 points per tooth
    offsets = [-0.35, -0.12, 0.12, 0.35]
    radii = [root_radius, outer_radius, outer_radius, root_radius]

    angle = base_angle + da * offsets[sub]
    r = radii[sub]

    prof_verts.append(bm.verts.new((math.cos(angle) * r, math.sin(angle) * r, 0)))

# Hole verts (bottom)
hole_verts = []
for i in range(hole_segments):
    angle = 2.0 * math.pi * i / hole_segments
    hole_verts.append(bm.verts.new((math.cos(angle) * hole_radius, math.sin(angle) * hole_radius, 0)))

bm.verts.ensure_lookup_table()

# Create face with hole using bmesh operations
# First, create outer face (temporarily solid)
face_outer = bm.faces.new(prof_verts)

# Create inner face (hole)
# To subtract, we can use bmesh.ops.contextual_create or just build manually with triangles/quads
# Cleanest approach for a single-mesh gear without boolean self-intersection issues:
# Bridge inner circle to outer profile using a triangulation strip.

bm.clear()

# Let's match hole_segments to a divisor or just use a direct vertex grid,
# Or even simpler: create the 3D shell directly.

# Re-initialize for direct 3D generation
verts_bottom_outer = []
verts_top_outer = []
verts_bottom_inner = []
verts_top_inner = []

for i in range(total_outer):
    t = i / 4
    base_angle = 2.0 * math.pi * (t // 1) / num_teeth
    sub = int(i % 4)
    da = 2.0 * math.pi / num_teeth
    offsets = [-0.35, -0.12, 0.12, 0.35]
    radii = [root_radius, outer_radius, outer_radius, root_radius]
    angle = base_angle + da * offsets[sub]
    r = radii[sub]

    verts_bottom_outer.append(bm.verts.new((math.cos(angle) * r, math.sin(angle) * r, -thickness / 2)))
    verts_top_outer.append(bm.verts.new((math.cos(angle) * r, math.sin(angle) * r, thickness / 2)))

for i in range(hole_segments):
    angle = 2.0 * math.pi * i / hole_segments
    x = math.cos(angle) * hole_radius
    y = math.sin(angle) * hole_radius
    verts_bottom_inner.append(bm.verts.new((x, y, -thickness / 2)))
    verts_top_inner.append(bm.verts.new((x, y, thickness / 2)))

bm.verts.ensure_lookup_table()

# 1. Outer perimeter walls (Quads)
for i in range(total_outer):
    next_i = (i + 1) % total_outer
    v0 = verts_bottom_outer[i]
    v1 = verts_bottom_outer[next_i]
    v2 = verts_top_outer[next_i]
    v3 = verts_top_outer[i]
    bm.faces.new((v0, v1, v2, v3))

# 2. Inner hole walls (Quads - note normal facing inward/outward)
for i in range(hole_segments):
    next_i = (i + 1) % hole_segments
    # Reversed order for inward-facing walls
    v0 = verts_bottom_inner[i]
    v1 = verts_top_inner[i]
    v2 = verts_top_inner[next_i]
    v3 = verts_bottom_inner[next_i]
    bm.faces.new((v0, v1, v2, v3))

# 3. Caps (Top and Bottom)
# Since hole_segments != total_outer, we bridge inner and outer circles via a triangulation fan/strip,
# or simply use bmesh.ops.bridge_loops for outer-to-inner if counts matched.
# Since counts don't match, let's create the caps by creating an N-gon with a hole for top and bottom.
# BMesh `faces.new` can accept a sequence of vertices for the outer boundary,
# but holes require `bmesh` internal loop structure or simpler:
# We can just triangulate thecap region between `verts_bottom_inner` and `verts_bottom_outer`
# using nearest-neighbor or a simple fan if we retopologize, OR we can make `hole_segments == total_outer`!

# -> PRO-TIP: Set hole_segments = total_outer (96 segments). Then direct 1-to-1 bridging works perfectly!
bm.clear()

res = num_teeth * 4  # 96 segments
verts_bottom_outer = []
verts_top_outer = []
verts_bottom_inner = []
verts_top_inner = []

for i in range(res):
    base_angle = 2.0 * math.pi * (i // 4) / num_teeth
    sub = i % 4
    da = 2.0 * math.pi / num_teeth
    offsets = [-0.35, -0.12, 0.12, 0.35]
    radii = [root_radius, outer_radius, outer_radius, root_radius]

    angle = base_angle + da * offsets[sub]
    r = radii[sub]

    # Outer profile
    verts_bottom_outer.append(bm.verts.new((math.cos(angle) * r, math.sin(angle) * r, -thickness / 2)))
    verts_top_outer.append(bm.verts.new((math.cos(angle) * r, math.sin(angle) * r, thickness / 2)))

    # Inner hole (matching vertex count for clean topology)
    hole_angle = 2.0 * math.pi * i / res
    hx = math.cos(hole_angle) * hole_radius
    hy = math.sin(hole_angle) * hole_radius
    verts_bottom_inner.append(bm.verts.new((hx, hy, -thickness / 2)))
    verts_top_inner.append(bm.verts.new((hx, hy, thickness / 2)))

bm.verts.ensure_lookup_table()

# Outer walls
for i in range(res):
    next_i = (i + 1) % res
    bm.faces.new(
        (
            verts_bottom_outer[i],
            verts_bottom_outer[next_i],
            verts_top_outer[next_i],
            verts_top_outer[i],
        )
    )

# Inner walls (reversed normals)
for i in range(res):
    next_i = (i + 1) % res
    bm.faces.new(
        (
            verts_bottom_inner[i],
            verts_top_inner[i],
            verts_top_inner[next_i],
            verts_bottom_inner[next_i],
        )
    )

# Bottom cap (quads connecting inner to outer)
for i in range(res):
    next_i = (i + 1) % res
    bm.faces.new(
        (
            verts_bottom_inner[i],
            verts_bottom_inner[next_i],
            verts_bottom_outer[next_i],
            verts_bottom_outer[i],
        )
    )

# Top cap (quads connecting outer to inner, reversed for normal orientation)
for i in range(res):
    next_i = (i + 1) % res
    bm.faces.new(
        (
            verts_top_inner[i],
            verts_top_outer[i],
            verts_top_outer[next_i],
            verts_top_inner[next_i],
        )
    )

# Finalize mesh
bm.normal_update()
bm.to_mesh(mesh)
bm.free()

# Set smooth shading for cylindrical/gear surfaces
bpy.ops.object.shade_smooth()
