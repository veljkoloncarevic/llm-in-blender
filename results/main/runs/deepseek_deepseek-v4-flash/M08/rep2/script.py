import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects from the scene
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Parameters
helix_radius = 1.0
height = 4.0
turns = 8
wire_radius = 0.15
segments = 256          # number of intervals along the helix
circle_verts = 32       # number of vertices in the circular cross-section

# Create new mesh and object
mesh = bpy.data.meshes.new("CoilSpringMesh")
obj = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(obj)

# Prepare bmesh
bm = bmesh.new()

total_angle = turns * 2.0 * math.pi
p = height / total_angle  # dz per radian

# Build rings of vertices
rings = []
for i in range(segments + 1):
    theta = total_angle * i / segments

    # Helix point
    pos = Vector((
        helix_radius * math.cos(theta),
        helix_radius * math.sin(theta),
        p * theta
    ))

    # Tangent vector
    tangent = Vector((
        -helix_radius * math.sin(theta),
        helix_radius * math.cos(theta),
        p
    )).normalized()

    # Frenet-like frame (perpendicular to tangent)
    normal = tangent.cross(Vector((0.0, 0.0, 1.0))).normalized()
    binormal = tangent.cross(normal).normalized()

    # Circular cross-section vertices
    ring_verts = []
    for j in range(circle_verts):
        phi = 2.0 * math.pi * j / circle_verts
        offset = normal * (wire_radius * math.cos(phi)) + binormal * (wire_radius * math.sin(phi))
        ring_verts.append(bm.verts.new(pos + offset))
    rings.append(ring_verts)

# Create quad faces between consecutive rings
for i in range(segments):
    current_ring = rings[i]
    next_ring = rings[i + 1]
    for j in range(circle_verts):
        j_next = (j + 1) % circle_verts
        v0 = current_ring[j]
        v1 = next_ring[j]
        v2 = next_ring[j_next]
        v3 = current_ring[j_next]
        bm.faces.new((v0, v1, v2, v3))

# Recalculate consistent outward normals
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Write bmesh to mesh
bm.to_mesh(mesh)
bm.free()
