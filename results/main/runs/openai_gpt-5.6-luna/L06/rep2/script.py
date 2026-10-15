import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
die_mat = bpy.data.materials.new("Ivory Die")
die_mat.diffuse_color = (0.82, 0.68, 0.42, 1.0)
die_mat.roughness = 0.38

pip_mat = bpy.data.materials.new("Dark Pips")
pip_mat.diffuse_color = (0.035, 0.018, 0.008, 1.0)
pip_mat.roughness = 0.3

# Main die cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
die = bpy.context.object
die.name = "Rounded Die"
die.data.materials.append(die_mat)

bevel = die.modifiers.new("Rounded Edges - 3 Segments", 'BEVEL')
bevel.width = 0.17
bevel.segments = 3
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.5
bevel.harden_normals = True

# Pip layouts, expressed as coordinates on a face
patterns = {
    1: [(0, 0)],
    2: [(-1, -1), (1, 1)],
    3: [(-1, -1), (0, 0), (1, 1)],
    4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
    6: [(-1, -1), (-1, 0), (-1, 1),
        (1, -1), (1, 0), (1, 1)],
}

# Face definitions: normal, first tangent, second tangent, pip value
faces = [
    (Vector((0, 0, 1)), Vector((1, 0, 0)), Vector((0, 1, 0)), 1),
    (Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, -1, 0)), 6),
    (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)), 2),
    (Vector((-1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, -1)), 5),
    (Vector((0, 1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1)), 3),
    (Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, -1)), 4),
]

pip_spacing = 0.36
pip_radius = 0.115
pip_depth_scale = 0.48
pip_surface = 0.865

for normal, tangent_u, tangent_v, value in faces:
    for a, b in patterns[value]:
        position = (
            normal * pip_surface
            + tangent_u * (a * pip_spacing)
            + tangent_v * (b * pip_spacing)
        )

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12,
            ring_count=6,
            radius=pip_radius,
            location=position
        )
        pip = bpy.context.object
        pip.name = "Pip"
        pip.data.materials.append(pip_mat)

        # Flatten the sphere along the face normal to make a shallow pip
        pip.scale = (1.0, 1.0, pip_depth_scale)
        pip.rotation_mode = 'QUATERNION'
        pip.rotation_quaternion = normal.to_track_quat('Z', 'Y')

        for polygon in pip.data.polygons:
            polygon.use_smooth = True
