import bpy
import bmesh
import mathutils


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def create_die():
    """Create the cube with a bevel modifier."""
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = "Die"

    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.segments = 3
    bevel.width = 0.2
    bevel.limit_method = 'NONE'
    bevel.affect = 'EDGES'
    bevel.profile = 0.5

    return obj


def create_pip(bm, pos, normal, radius=0.15, depth=0.05, segments=8):
    """Add a shallow cylinder oriented along the face normal."""
    quat = mathutils.Vector((0, 0, 1)).rotation_difference(normal)
    mat = mathutils.Matrix.Translation(pos) @ quat.to_matrix().to_4x4()

    bmesh.ops.create_cone(
        bm,
        diameter1=radius,
        diameter2=radius,
        depth=depth,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        matrix=mat,
    )


def add_pips():
    """Add all pips as a single mesh object."""
    # Face data: (normal, local U axis, local V axis, pip positions)
    faces = [
        (mathutils.Vector((0, 0, 1)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)),
         [(0, 0)]),  # 1 on +Z
        (mathutils.Vector((0, 0, -1)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)),
         [(-0.5, -0.5), (-0.5, 0), (-0.5, 0.5), (0.5, -0.5), (0.5, 0), (0.5, 0.5)]),  # 6 on -Z
        (mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1)),
         [(-0.5, -0.5), (0.5, 0.5)]),  # 2 on +X
        (mathutils.Vector((-1, 0, 0)), mathutils.Vector((0, 1, 0)), mathutils.Vector((0, 0, 1)),
         [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5), (0, 0)]),  # 5 on -X
        (mathutils.Vector((0, 1, 0)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 0, 1)),
         [(-0.5, -0.5), (0, 0), (0.5, 0.5)]),  # 3 on +Y
        (mathutils.Vector((0, -1, 0)), mathutils.Vector((1, 0, 0)), mathutils.Vector((0, 0, 1)),
         [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]),  # 4 on -Y
    ]

    mesh = bpy.data.meshes.new("Pips")
    obj = bpy.data.objects.new("Pips", mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()
    for normal, u_axis, v_axis, pattern in faces:
        face_center = normal * 1.0  # cube extends from -1 to 1
        for du, dv in pattern:
            pos = face_center + du * u_axis + dv * v_axis
            create_pip(bm, pos, normal)

    bm.to_mesh(mesh)
    bm.free()


def main():
    clear_scene()
    create_die()
    add_pips()
    bpy.context.view_layer.update()


if __name__ == "__main__":
    main()
