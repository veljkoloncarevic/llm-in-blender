import bpy
import math
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Spring parameters
major_radius = 1.0
height = 4.0
turns = 8
wire_radius = 0.1

# Mesh resolution
helix_segments = 400      # number of segments along the helix
cross_sides = 24          # number of sides for the circular cross-section

total_theta = 2 * math.pi * turns
c = height / total_theta  # dz/dtheta for the helix

bm = bmesh.new()

# Create all vertices: (helix_segments+1) rings, each with cross_sides vertices
for i in range(helix_segments + 1):
    theta = total_theta * i / helix_segments
    center = Vector((
        major_radius * math.cos(theta),
        major_radius * math.sin(theta),
        c * theta
    ))

    # Tangent vector at this point
    tangent = Vector((
        -major_radius * math.sin(theta),
        major_radius * math.cos(theta),
        c
    ))
    tangent.normalize()

    # Radial normal in the XY plane (always perpendicular to tangent)
    normal = Vector((math.cos(theta), math.sin(theta), 0.0))

    # Binormal to complete the perpendicular basis
    binormal = tangent.cross(normal)
    binormal.normalize()

    # Place the cross-section vertices
    for j in range(cross_sides):
        phi = 2 * math.pi * j / cross_sides
        offset = normal * (wire_radius * math.cos(phi)) + binormal * (wire_radius * math.sin(phi))
        bm.verts.new(center + offset)

bm.verts.ensure_lookup_table()

# Create faces connecting consecutive rings
for i in range(helix_segments):
    for j in range(cross_sides):
        v0 = bm.verts[i * cross_sides + j]
        v1 = bm.verts[i * cross_sides + (j + 1) % cross_sides]
        v2 = bm.verts[(i + 1) * cross_sides + (j + 1) % cross_sides]
        v3 = bm.verts[(i + 1) * cross_sides + j]
        face = bm.faces.new((v0, v1, v2, v3))
        face.smooth = True

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Create mesh object
mesh_data = bpy.data.meshes.new("CoilSpring")
bm.to_mesh(mesh_data)
bm.free()

obj = bpy.data.objects.new("CoilSpring", mesh_data)
bpy.context.collection.objects.link(obj)
