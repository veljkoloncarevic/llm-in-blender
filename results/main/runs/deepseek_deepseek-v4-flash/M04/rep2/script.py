import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Torus knot parameters
p, q = 2, 3
R = 2.0
r = 1.0
tube_radius = 0.15

# Resolution
N_path = 1000  # segments around the knot
N_circle = 24  # segments around the tube cross-section

# Compute curve points and frames
path = []
for i in range(N_path):
    t = 2.0 * math.pi * i / float(N_path)
    u = p * t
    v = q * t

    cos_u = math.cos(u)
    sin_u = math.sin(u)
    cos_v = math.cos(v)
    sin_v = math.sin(v)

    # Position on torus knot
    pos = Vector((
        (R + r * cos_v) * cos_u,
        (R + r * cos_v) * sin_u,
        r * sin_v
    ))

    # Tangent vector (derivative)
    dx_dt = -(R + r * cos_v) * p * sin_u - r * q * sin_v * cos_u
    dy_dt = (R + r * cos_v) * p * cos_u - r * q * sin_v * sin_u
    dz_dt = r * q * cos_v
    tangent = Vector((dx_dt, dy_dt, dz_dt))
    tangent.normalize()

    # Normal to the underlying torus surface (also perpendicular to the tangent)
    normal = Vector((cos_v * cos_u, cos_v * sin_u, sin_v))
    normal.normalize()

    # Binormal completes the frame
    binormal = tangent.cross(normal)
    binormal.normalize()

    path.append((pos, tangent, normal, binormal))

# Build the tube mesh
mesh = bpy.data.meshes.new("TorusKnot")
bm = bmesh.new()

# Create cross-section vertices for each path point
verts = []
for pos, tangent, normal, binormal in path:
    ring = []
    for j in range(N_circle):
        theta = 2.0 * math.pi * j / float(N_circle)
        offset = (math.cos(theta) * normal + math.sin(theta) * binormal) * tube_radius
        v = bm.verts.new(pos + offset)
        ring.append(v)
    verts.append(ring)

# Create quad faces between adjacent rings
for i in range(N_path):
    i_next = (i + 1) % N_path
    for j in range(N_circle):
        j_next = (j + 1) % N_circle
        face = bm.faces.new((
            verts[i][j],
            verts[i][j_next],
            verts[i_next][j_next],
            verts[i_next][j],
        ))
        face.smooth = True

bm.normal_update()
bm.to_mesh(mesh)
bm.free()

# Link the mesh to the scene
obj = bpy.data.objects.new("TorusKnot", mesh)
bpy.context.collection.objects.link(obj)
