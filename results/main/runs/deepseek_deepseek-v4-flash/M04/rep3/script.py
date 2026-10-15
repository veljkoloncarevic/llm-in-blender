import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Torus knot parameters
p = 2
q = 3
R = 2.0          # major radius of the torus
r = 0.5          # minor radius of the torus on which the knot lies
tube_radius = 0.1
segments = 1000  # number of rings along the curve
circle_segments = 16  # number of vertices around the tube

def knot_point(t):
    """Evaluate the (p,q) torus knot at parameter t in [0, 2π]."""
    x = (R + r * math.cos(q * t)) * math.cos(p * t)
    y = (R + r * math.cos(q * t)) * math.sin(p * t)
    z = r * math.sin(q * t)
    return Vector((x, y, z))

def knot_tangent(t):
    """Derivative of the torus knot curve."""
    cp = p * t
    cq = q * t
    dx = -p * (R + r * math.cos(cq)) * math.sin(cp) - r * q * math.sin(cq) * math.cos(cp)
    dy =  p * (R + r * math.cos(cq)) * math.cos(cp) - r * q * math.sin(cq) * math.sin(cp)
    dz =  r * q * math.cos(cq)
    return Vector((dx, dy, dz))

# Precompute frames: position, normal, binormal
frames = []
for i in range(segments):
    t = i * 2.0 * math.pi / segments
    T = knot_tangent(t)
    T.normalize()

    # Use global Z as reference; it is never parallel to T for this knot.
    N = T.cross(Vector((0.0, 0.0, 1.0)))
    if N.length_squared < 1e-12:
        N = T.cross(Vector((0.0, 1.0, 0.0)))
    N.normalize()

    B = T.cross(N)
    frames.append((knot_point(t), N, B))

# Build mesh with bmesh
bm = bmesh.new()

rings = []
for i in range(segments):
    center, N, B = frames[i]
    ring = []
    for j in range(circle_segments):
        angle = j * 2.0 * math.pi / circle_segments
        offset = N * math.cos(angle) + B * math.sin(angle)
        vert = bm.verts.new(center + offset * tube_radius)
        ring.append(vert)
    rings.append(ring)

# Create quad faces between consecutive rings
for i in range(segments):
    i_next = (i + 1) % segments
    for j in range(circle_segments):
        j_next = (j + 1) % circle_segments
        v1 = rings[i][j]
        v2 = rings[i][j_next]
        v3 = rings[i_next][j_next]
        v4 = rings[i_next][j]
        bm.faces.new((v1, v2, v3, v4))

# Create mesh object
mesh = bpy.data.meshes.new("TorusKnot")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("TorusKnot", mesh)
bpy.context.collection.objects.link(obj)
