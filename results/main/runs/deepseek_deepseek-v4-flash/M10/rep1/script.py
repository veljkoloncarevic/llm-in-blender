import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def build_chain():
    clear_scene()

    bm = bmesh.new()

    n_links = 12
    a = 1.0          # major semi-axis along chain axis
    b = 0.6          # minor semi-axis of the oval
    tube_r = 0.12    # tube radius
    spacing = 1.25   # distance between link centres along chain axis

    path_segments = 48
    profile_segments = 12

    chain_axis = Vector((1.0, 0.0, 0.0))
    centre_offset = (n_links - 1) * spacing * 0.5

    for i in range(n_links):
        theta = 0.0 if i % 2 == 0 else math.pi * 0.5

        # Minor axis of the ellipse: Z for vertical links, Y for horizontal links.
        minor_axis = Vector((0.0, math.sin(theta), math.cos(theta)))
        centre = Vector((i * spacing - centre_offset, 0.0, 0.0))

        rings = []

        for p in range(path_segments):
            t = 2.0 * math.pi * p / path_segments

            # Point on the oval centreline.
            path_point = (
                centre
                + chain_axis * (a * math.cos(t))
                + minor_axis * (b * math.sin(t))
            )

            # Tangent and curve normal at this path point.
            tangent_raw = (
                chain_axis * (-a * math.sin(t))
                + minor_axis * (b * math.cos(t))
            )
            tangent = tangent_raw.normalized()

            accel_raw = (
                chain_axis * (-a * math.cos(t))
                + minor_axis * (-b * math.sin(t))
            )
            normal_raw = accel_raw - accel_raw.dot(tangent) * tangent
            normal = normal_raw.normalized()
            binormal = tangent.cross(normal).normalized()

            ring = []
            for q in range(profile_segments):
                phi = 2.0 * math.pi * q / profile_segments
                offset = normal * (tube_r * math.cos(phi)) + binormal * (tube_r * math.sin(phi))
                ring.append(bm.verts.new(path_point + offset))

            rings.append(ring)

        for p in range(path_segments):
            p2 = (p + 1) % path_segments
            ring_a = rings[p]
            ring_b = rings[p2]

            for q in range(profile_segments):
                q2 = (q + 1) % profile_segments

                v0 = ring_a[q]
                v1 = ring_a[q2]
                v2 = ring_b[q2]
                v3 = ring_b[q]

                try:
                    bm.faces.new((v0, v1, v2, v3))
                except ValueError:
                    pass

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    for f in bm.faces:
        f.smooth = True

    mesh = bpy.data.meshes.new("ChainMesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    obj = bpy.data.objects.new("Chain", mesh)
    bpy.context.scene.collection.objects.link(obj)


build_chain()
