import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Parameters
p = 2
q = 3
R = 2.0          # torus major radius
r = 1.0          # torus minor radius
tube_radius = 0.1

N = 512          # segments along the curve
S = 24           # sides around the tube

# Precompute frames using the torus parameterization
points = []
frames = []  # (position, tangent_hat, normal1, normal2)

for i in range(N):
    t = 2.0 * math.pi * i / N
    theta = p * t
    phi = q * t

    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    cos_phi = math.cos(phi)
    sin_phi = math.sin(phi)

    center = R + r * cos_phi
    pos = Vector((
        center * cos_theta,
        center * sin_theta,
        r * sin_phi
    ))

    # Derivative with respect to t
    dtheta = p
    dphi = q
    dx = -r * sin_phi * dphi * cos_theta - center * sin_theta * dtheta
    dy = -r * sin_phi * dphi * sin_theta + center * cos_theta * dtheta
    dz = r * cos_phi * dphi
    tangent = Vector((dx, dy, dz)).normalized()

    # Torus surface normal (radial outward)
    radial = Vector((cos_theta * cos_phi, sin_theta * cos_phi, sin_phi))

    # Orthogonalize radial against tangent
    radial -= radial.dot(tangent) * tangent
    radial.normalize()

    binormal = tangent.cross(radial).normalized()
    frames.append((pos, tangent, radial, binormal))

# Build mesh
bm = bmesh.new()

for pos, tangent, radial, binormal in frames:
    for k in range(S):
        angle = 2.0 * math.pi * k / S
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        offset = tube_radius * (cos_a * radial + sin_a * binormal)
        bm.verts.new(pos + offset)

bm.verts.ensure_lookup_table()

# Add quad faces
for i in range(N):
    for k in range(S):
        v0 = bm.verts[i * S + k]
        v1 = bm.verts[i * S + (k + 1) % S]
        v2 = bm.verts[((i + 1) % N) * S + (k + 1) % S]
        v3 = bm.verts[((i + 1) % N) * S + k]
        bm.faces.new((v0, v1, v2, v3))

# Recalculate normals so they point outward
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Create mesh object
me = bpy.data.meshes.new("TorusKnotMesh")
bm.to_mesh(me)
bm.free()

obj = bpy.data.objects.new("TorusKnot", me)
bpy.context.collection.objects.link(obj)
