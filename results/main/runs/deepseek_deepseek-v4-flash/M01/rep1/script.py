import bpy
import bmesh
import math
from mathutils import Vector


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_step_mesh(num_segments, inner_r, outer_r, step_angle, thickness):
    mesh = bpy.data.meshes.new("Step")
    bm = bmesh.new()

    n = num_segments
    angles = [step_angle * i / n for i in range(n + 1)]

    top_in = [bm.verts.new((inner_r * math.cos(a), inner_r * math.sin(a), 0)) for a in angles]
    top_out = [bm.verts.new((outer_r * math.cos(a), outer_r * math.sin(a), 0)) for a in angles]
    bot_in = [bm.verts.new((inner_r * math.cos(a), inner_r * math.sin(a), -thickness)) for a in angles]
    bot_out = [bm.verts.new((outer_r * math.cos(a), outer_r * math.sin(a), -thickness)) for a in angles]

    for i in range(n):
        bm.faces.new((top_in[i], top_out[i], top_out[i + 1], top_in[i + 1]))
        bm.faces.new((bot_in[i + 1], bot_out[i + 1], bot_out[i], bot_in[i]))
        bm.faces.new((top_in[i], top_in[i + 1], bot_in[i + 1], bot_in[i]))
        bm.faces.new((top_out[i], bot_out[i], bot_out[i + 1], top_out[i + 1]))

    bm.faces.new((top_in[0], top_out[0], bot_out[0], bot_in[0]))
    bm.faces.new((top_in[n], bot_in[n], bot_out[n], top_out[n]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def create_column_mesh(radius, height, segments):
    mesh = bpy.data.meshes.new("Column")
    bm = bmesh.new()

    bottom = []
    top = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        x = radius * math.cos(a)
        y = radius * math.sin(a)
        bottom.append(bm.verts.new((x, y, 0)))
        top.append(bm.verts.new((x, y, height)))

    for i in range(segments):
        i2 = (i + 1) % segments
        bm.faces.new((bottom[i], bottom[i2], top[i2], top[i]))

    b_center = bm.verts.new((0, 0, 0))
    t_center = bm.verts.new((0, 0, height))

    for i in range(segments):
        i2 = (i + 1) % segments
        bm.faces.new((bottom[i], bottom[i2], b_center))
        bm.faces.new((top[i], t_center, top[i2]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def create_handrail_mesh(radius, tube_radius, offset_z, total_height, path_segments, circle_segments):
    mesh = bpy.data.meshes.new("Handrail")
    bm = bmesh.new()

    theta_start = 0.0
    theta_end = 2.0 * math.pi
    pitch = total_height / (theta_end - theta_start)

    rings = []

    for j in range(path_segments + 1):
        theta = theta_start + (theta_end - theta_start) * j / path_segments
        z = offset_z + pitch * (theta - theta_start)

        center = Vector((radius * math.cos(theta), radius * math.sin(theta), z))
        tangent = Vector((-radius * math.sin(theta), radius * math.cos(theta), pitch))
        T = tangent.normalized()

        up = Vector((0, 0, 1))
        N = up - T * T.dot(up)
        N.normalize()
        B = T.cross(N)

        ring = []
        for c in range(circle_segments):
            phi = 2 * math.pi * c / circle_segments
            v = center + tube_radius * (math.cos(phi) * N + math.sin(phi) * B)
            ring.append(bm.verts.new(v))
        rings.append(ring)

    for j in range(path_segments):
        ring_a = rings[j]
        ring_b = rings[j + 1]
        for c in range(circle_segments):
            c2 = (c + 1) % circle_segments
            bm.faces.new((ring_a[c], ring_a[c2], ring_b[c2], ring_b[c]))

    start_center = bm.verts.new((radius * math.cos(theta_start), radius * math.sin(theta_start), offset_z))
    for c in range(circle_segments):
        c2 = (c + 1) % circle_segments
        bm.faces.new((rings[0][c], rings[0][c2], start_center))

    end_center = bm.verts.new((
        radius * math.cos(theta_end),
        radius * math.sin(theta_end),
        offset_z + total_height
    ))
    for c in range(circle_segments):
        c2 = (c + 1) % circle_segments
        bm.faces.new((rings[-1][c], rings[-1][c2], end_center))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def main():
    clear_scene()

    num_steps = 24
    step_angle = math.radians(15)
    rise = 0.2

    inner_r = 0.3
    outer_r = 1.5
    step_thickness = 0.05

    handrail_offset = 0.9
    handrail_total_height = num_steps * rise
    column_height = 6.0

    step_mesh = create_step_mesh(8, inner_r, outer_r, step_angle, step_thickness)

    for i in range(num_steps):
        obj = bpy.data.objects.new(f"Step_{i:02d}", step_mesh)
        bpy.context.collection.objects.link(obj)
        obj.rotation_euler = (0, 0, i * step_angle)
        obj.location = (0, 0, i * rise)

    column_mesh = create_column_mesh(inner_r, column_height, 32)
    col_obj = bpy.data.objects.new("Column", column_mesh)
    bpy.context.collection.objects.link(col_obj)

    handrail_mesh = create_handrail_mesh(outer_r, 0.03, handrail_offset, handrail_total_height, 240, 12)
    rail_obj = bpy.data.objects.new("Handrail", handrail_mesh)
    bpy.context.collection.objects.link(rail_obj)


if __name__ == "__main__":
    main()
