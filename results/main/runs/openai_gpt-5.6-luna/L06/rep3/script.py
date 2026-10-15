import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
die_mat = bpy.data.materials.new("Ivory Die")
die_mat.diffuse_color = (0.82, 0.78, 0.66, 1.0)
die_mat.roughness = 0.42

pip_mat = bpy.data.materials.new("Dark Pips")
pip_mat.diffuse_color = (0.025, 0.018, 0.012, 1.0)
pip_mat.roughness = 0.3

# Main die
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
die = bpy.context.object
die.name = "Rounded Die"
die.data.materials.append(die_mat)

bevel = die.modifiers.new("Rounded Edges - 3 Segments", 'BEVEL')
bevel.width = 0.18
bevel.segments = 3
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.523599
bevel.harden_normals = True

die.data.set_sharp_from_angle(angle=0.523599)

# Pip layouts in local face coordinates
layouts = {
    1: [(0.0, 0.0)],
    2: [(-0.42, 0.42), (0.42, -0.42)],
    3: [(-0.42, 0.42), (0.0, 0.0), (0.42, -0.42)],
    4: [(-0.42, -0.42), (-0.42, 0.42),
        (0.42, -0.42), (0.42, 0.42)],
    5: [(-0.42, -0.42), (-0.42, 0.42),
        (0.0, 0.0), (0.42, -0.42),
        (0.42, 0.42)],
    6: [(-0.42, -0.42), (-0.42, 0.0), (-0.42, 0.42),
        (0.42, -0.42), (0.42, 0.0), (0.42, 0.42)],
}

# Face definitions: number, outward normal, face-local U axis, face-local V axis
faces = [
    (1, Vector((0, 0, 1)),  Vector((1, 0, 0)), Vector((0, 1, 0))),
    (6, Vector((0, 0, -1)), Vector((-1, 0, 0)), Vector((0, 1, 0))),
    (2, Vector((1, 0, 0)),  Vector((0, 1, 0)), Vector((0, 0, 1))),
    (5, Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1))),
    (3, Vector((0, 1, 0)),  Vector((-1, 0, 0)), Vector((0, 0, 1))),
    (4, Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1))),
]

# Create shallow cylindrical pips
for number, normal, axis_u, axis_v in faces:
    for u, v in layouts[number]:
        position = normal * 1.018 + axis_u * u + axis_v * v

        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12,
            radius=0.105,
            depth=0.065,
            end_fill_type='NGON',
            location=position
        )
        pip = bpy.context.object
        pip.name = f"Face {number} Pip"
        pip.data.materials.append(pip_mat)

        # Default cylinder axis is Z; align it to the face normal
        pip.rotation_mode = 'QUATERNION'
        pip.rotation_quaternion = normal.to_track_quat('Z', 'Y')

        for polygon in pip.data.polygons:
            polygon.use_smooth = True

# Smooth the die surface while retaining crisp face shading
for polygon in die.data.polygons:
    polygon.use_smooth = True
