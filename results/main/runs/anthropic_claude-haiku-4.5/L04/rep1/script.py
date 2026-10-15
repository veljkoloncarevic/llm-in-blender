import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new mesh and object for the pawn
pawn_mesh = bpy.data.meshes.new("PawnMesh")
pawn_obj = bpy.data.objects.new("Pawn", pawn_mesh)
bpy.context.collection.objects.link(pawn_obj)
bpy.context.view_layer.objects.active = pawn_obj
pawn_obj.select_set(True)

# Create bmesh for the pawn
bm = bmesh.new()

# Current Z position for stacking components
current_z = 0

# 1. Wide cylinder base (8 vertices, low poly)
base_radius = 0.4
base_height = 0.15
base_verts = []
for i in range(8):
    angle = (i / 8) * 2 * 3.14159
    x = base_radius * (1 + 0.1 * (i % 2))  # Slight variation for visual interest
    y = base_radius * (1 + 0.1 * (i % 2))
    import math
    x = base_radius * math.cos(angle)
    y = base_radius * math.sin(angle)
    base_verts.append(bm.verts.new((x, y, current_z)))

# Top ring of base
base_verts_top = []
for i in range(8):
    angle = (i / 8) * 2 * 3.14159
    import math
    x = base_radius * math.cos(angle)
    y = base_radius * math.sin(angle)
    base_verts_top.append(bm.verts.new((x, y, current_z + base_height)))

# Create base cylinder faces
for i in range(8):
    next_i = (i + 1) % 8
    bm.faces.new([base_verts[i], base_verts[next_i], base_verts_top[next_i], base_verts_top[i]])

# Top face of base
bm.faces.new(base_verts_top)

current_z += base_height

# 2. Torus collar (simple torus using 8x6 grid)
torus_major_radius = 0.35
torus_minor_radius = 0.06
torus_segments = 8
torus_rings = 6

torus_verts = []
for ring in range(torus_rings):
    ring_verts = []
    ring_angle = (ring / torus_rings) * 2 * 3.14159
    import math
    ring_center_z = current_z + torus_minor_radius * math.sin(ring_angle)
    ring_center_dist = torus_major_radius + torus_minor_radius * math.cos(ring_angle)
    
    for seg in range(torus_segments):
        seg_angle = (seg / torus_segments) * 2 * 3.14159
        x = ring_center_dist * math.cos(seg_angle)
        y = ring_center_dist * math.sin(seg_angle)
        ring_verts.append(bm.verts.new((x, y, ring_center_z)))
    torus_verts.append(ring_verts)

# Create torus faces
for ring in range(torus_rings - 1):
    for seg in range(torus_segments):
        next_seg = (seg + 1) % torus_segments
        v1 = torus_verts[ring][seg]
        v2 = torus_verts[ring][next_seg]
        v3 = torus_verts[ring + 1][next_seg]
        v4 = torus_verts[ring + 1][seg]
        bm.faces.new([v1, v2, v3, v4])

current_z += torus_minor_radius * 2

# 3. Tapered cylinder body (cone-like)
body_base_radius = 0.3
body_top_radius = 0.15
body_height = 0.6
body_segments = 8

body_base_verts = []
for i in range(body_segments):
    angle = (i / body_segments) * 2 * 3.14159
    import math
    x = body_base_radius * math.cos(angle)
    y = body_base_radius * math.sin(angle)
    body_base_verts.append(bm.verts.new((x, y, current_z)))

body_top_verts = []
for i in range(body_segments):
    angle = (i / body_segments) * 2 * 3.14159
    import math
    x = body_top_radius * math.cos(angle)
    y = body_top_radius * math.sin(angle)
    body_top_verts.append(bm.verts.new((x, y, current_z + body_height)))

# Create tapered body faces
for i in range(body_segments):
    next_i = (i + 1) % body_segments
    bm.faces.new([body_base_verts[i], body_base_verts[next_i], body_top_verts[next_i], body_top_verts[i]])

current_z += body_height

# 4. Sphere head (UV sphere, 6x6 segments)
head_radius = 0.2
head_segments = 6
head_rings = 6

head_verts = []
# Top pole
top_pole = bm.verts.new((0, 0, current_z + head_radius))

# Middle rings
for ring in range(1, head_rings):
    ring_angle = (ring / head_rings) * 3.14159
    import math
    ring_z = current_z + head_radius * math.cos(ring_angle)
    ring_radius = head_radius * math.sin(ring_angle)
    ring_verts = []
    
    for seg in range(head_segments):
        seg_angle = (seg / head_segments) * 2 * 3.14159
        x = ring_radius * math.cos(seg_angle)
        y = ring_radius * math.sin(seg_angle)
        ring_verts.append(bm.verts.new((x, y, ring_z)))
    head_verts.append(ring_verts)

# Bottom pole
bottom_pole = bm.verts.new((0, 0, current_z - head_radius))

# Create sphere faces
# Top cap
for seg in range(head_segments):
    next_seg = (seg + 1) % head_segments
    bm.faces.new([top_pole, head_verts[0][seg], head_verts[0][next_seg]])

# Middle bands
for ring in range(len(head_verts) - 1):
    for seg in range(head_segments):
        next_seg = (seg + 1) % head_segments
        v1 = head_verts[ring][seg]
        v2 = head_verts[ring][next_seg]
        v3 = head_verts[ring + 1][next_seg]
        v4 = head_verts[ring + 1][seg]
        bm.faces.new([v1, v2, v3, v4])

# Bottom cap
for seg in range(head_segments):
    next_seg = (seg + 1) % head_segments
    bm.faces.new([head_verts[-1][seg], bottom_pole, head_verts[-1][next_seg]])

# Finalize mesh
bm.to_mesh(pawn_mesh)
bm.free()

# Update mesh
pawn_mesh.update()

# Center the pawn at origin
pawn_obj.location = (0, 0, 0)
