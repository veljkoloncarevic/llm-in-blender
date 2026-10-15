import bpy
import bmesh
from mathutils import Vector, Matrix


def clear_scene():
    if len(bpy.data.objects) == 0:
        return
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_cube():
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.active_object
    obj.name = "Die"

    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = 3
    bevel.width = 0.15

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def get_basis(normal):
    normal = Vector(normal).normalized()
    if abs(normal.z) < 0.9:
        v = Vector((0, 0, 1))
    else:
        v = Vector((0, 1, 0))
    v = v - normal * v.dot(normal)
    v.normalize()
    u = v.cross(normal)
    return u, v


def add_pips(obj):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    patterns = {
        1: [(0, 0)],
        2: [(-0.4, -0.4), (0.4, 0.4)],
        3: [(-0.4, -0.4), (0, 0), (0.4, 0.4)],
        4: [(-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)],
        5: [(-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4), (0, 0)],
        6: [(-0.4, -0.4), (0.4, -0.4), (-0.4, 0), (0.4, 0), (-0.4, 0.4), (0.4, 0.4)],
    }

    face_numbers = [
        ((1, 0, 0), 1),
        ((-1, 0, 0), 6),
        ((0, 1, 0), 2),
        ((0, -1, 0), 5),
        ((0, 0, 1), 3),
        ((0, 0, -1), 4),
    ]

    radius = 0.15
    depth = 0.1
    segments = 12

    for n_vec, number in face_numbers:
        normal = Vector(n_vec)
        face_center = normal  # cube half-size = 1
        u_axis, v_axis = get_basis(normal)

        for u, v in patterns[number]:
            pip_pos = face_center + u_axis * u + v_axis * v

            z_axis = Vector((0, 0, 1))
            q = z_axis.rotation_difference(normal)
            rot = q.to_matrix().to_4x4()
            trans = Matrix.Translation(pip_pos - normal * (depth / 2.0))
            matrix = trans @ rot

            bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                cap_tris=False,
                segments=segments,
                diameter1=radius,
                diameter2=radius,
                depth=depth,
                matrix=matrix,
            )

    bm.to_mesh(mesh)
    mesh.update()
    bm.free()


def main():
    clear_scene()
    obj = create_cube()
    add_pips(obj)


if __name__ == "__main__":
    main()
