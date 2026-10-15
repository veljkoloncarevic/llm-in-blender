import bpy
import bmesh
import math
import mathutils


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def add_column(bm, radius, height, segments=32):
    mat = mathutils.Matrix.Translation((0.0, 0.0, height * 0.5))
    bmesh.ops.create_cylinder(
        bm,
        segments=segments,
        radius=radius,
        depth=height,
        cap_ends=True,
        cap_tris=False,
        matrix=mat
    )


def add_step(bm, angle, inner_r, outer_r, z_bot, z_top, arc_segments=8):
    start = angle
    end = angle + math.radians(15.0)

    ib = []
    ob = []
    it = []
    ot = []

    for k in range(arc_segments + 1):
        a = start + (end - start) * k / arc_segments
        c = math.cos(a)
        s = math.sin(a)

        ib.append(bm.verts.new((inner_r * c, inner_r * s, z_bot)))
        ob.append(bm.verts.new((outer_r * c, outer_r * s, z_bot)))
        it.append(bm.verts.new((inner_r * c, inner_r * s, z_top)))
        ot.append(bm.verts.new((outer_r * c, outer_r * s, z_top)))

    # Top face (normal +Z)
    top_verts = ot + list(reversed(it))
    bm.faces.new(top_verts)

    # Bottom face (normal -Z)
    bottom_verts = ib + list(reversed(ob))
    bm.faces.new(bottom_verts)

    # Outer curved side
    for k in range(arc_segments):
        bm.faces.new((ob[k], ob[k + 1], ot[k + 1], ot[k]))

    # Inner curved side
    for k in range(arc_segments):
        bm.faces.new((it[k], it[k + 1], ib[k + 1], ib[k]))

    # Start radial side
    bm.faces.new((it[0], ot[0], ob[0], ib[0]))

    # End radial side
    bm.faces.new((ib[-1], ob[-1], ot[-1], it[-1]))


def add_handrail(bm, outer_r, total_height, rail_offset, rail_radius,
                 circle_seg=12, path_seg=200):
    rows = []

    for i in range(path_seg + 1):
        t = i / path_seg
        angle = 2.0 * math.pi * t

        cx = outer_r * math.cos(angle)
        cy = outer_r * math.sin(angle)
        cz = rail_offset + total_height * t

        d = mathutils.Vector((
            -outer_r * 2.0 * math.pi * math.sin(angle),
            outer_r * 2.0 * math.pi * math.cos(angle),
            total_height
        ))
        d.normalize()

        up = mathutils.Vector((0.0, 0.0, 1.0))
        right = d.cross(up)
        if right.length_squared < 1e-12:
            right = mathutils.Vector((1.0, 0.0, 0.0))
        else:
            right.normalize()

        up2 = right.cross(d)
        up2.normalize()

        row = []
        for j in range(circle_seg):
            theta = 2.0 * math.pi * j / circle_seg
            off = right * (rail_radius * math.cos(theta)) + up2 * (rail_radius * math.sin(theta))
            row.append(bm.verts.new((cx + off.x, cy + off.y, cz + off.z)))

        rows.append(row)

    # Side quads
    for i in range(path_seg):
        for j in range(circle_seg):
            j2 = (j + 1) % circle_seg
            v0 = rows[i][j]
            v1 = rows[i][j2]
            v2 = rows[i + 1][j2]
            v3 = rows[i + 1][j]
            bm.faces.new((v0, v1, v2, v3))

    # Start cap
    bm.faces.new(rows[0])
    # End cap
    bm.faces.new(list(reversed(rows[-1])))


def main():
    clear_scene()

    bm = bmesh.new()

    num_steps = 24
    angle_step = 15.0
    height_step = 0.2
    total_height = num_steps * height_step

    column_radius = 1.0
    inner_radius = column_radius + 0.01
    outer_radius = 3.0
    step_thickness = 0.05

    # Central cylindrical column
    add_column(bm, column_radius, total_height, segments=32)

    # 24 steps
    for i in range(num_steps):
        angle = math.radians(i * angle_step)
        z_bot = i * height_step
        z_top = z_bot + step_thickness
        add_step(bm, angle, inner_radius, outer_radius, z_bot, z_top, arc_segments=8)

    # Helical handrail along the outer edge
    add_handrail(
        bm,
        outer_radius,
        total_height,
        rail_offset=1.0,
        rail_radius=0.06,
        circle_seg=12,
        path_seg=200
    )

    # Create mesh object
    mesh = bpy.data.meshes.new("SpiralStaircase")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("SpiralStaircase", mesh)
    bpy.context.collection.objects.link(obj)


if __name__ == "__main__":
    main()
