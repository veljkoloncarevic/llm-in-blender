import bpy
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
ivory = bpy.data.materials.new("Die Ivory")
ivory.diffuse_color = (0.82, 0.72, 0.52, 1.0)
ivory.roughness = 0.38

pip_material = bpy.data.materials.new("Pip Dark")
pip_material.diffuse_color = (0.025, 0.018, 0.012, 1.0)
pip_material.roughness = 0.5

# Main die
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
die = bpy.context.object
die.name = "Rounded Die"
die.data.materials.append(ivory)

for polygon in die.data.polygons:
    polygon.use_smooth = True

bevel = die.modifiers.new("Rounded Edges - 3 Segments", 'BEVEL')
bevel.width = 0.18
bevel.segments = 3
bevel.limit_method = 'ANGLE'
bevel.angle_limit = 0.35
bevel.harden_normals = True

# Pip layouts in 2D face coordinates
layouts = {
    1: [(0, 0)],
    2: [(-1, 1), (1, -1)],
    3: [(-1, 1), (0, 0), (1, -1)],
    4: [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    5: [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)],
    6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
}

# Face definitions: normal, tangent U, tangent V, value
faces = [
    (Vector((0, 0, 1)),  Vector((1, 0, 0)), Vector((0, 1, 0)), 1),
    (Vector((0, 0, -1)), Vector((-1, 0, 0)), Vector((0, 1, 0)), 6),
    (Vector((1, 0, 0)),  Vector((0, 1, 0)), Vector((0, 0, 1)), 3),
    (Vector((-1, 0, 0)), Vector((0, -1, 0)), Vector((0, 0, 1)), 4),
    (Vector((0, 1, 0)),  Vector((-1, 0, 0)), Vector((0, 0, 1)), 2),
    (Vector((0, -1, 0)), Vector((1, 0, 0)), Vector((0, 0, 1)), 5),
]

pip_spacing = 0.40

for normal, tangent_u, tangent_v, value in faces:
    for u, v in layouts[value]:
        position = normal * 0.985
        position += tangent_u * (u * pip_spacing)
        position += tangent_v * (v * pip_spacing)

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=8,
            ring_count=4,
            radius=1.0,
            location=position
        )
        pip = bpy.context.object
        pip.name = "Pip_%d" % value
        pip.data.materials.append(pip_material)

        # Flatten each sphere against its die face for a shallow pip.
        pip.scale = (0.135, 0.135, 0.055)
        pip.rotation_mode = 'QUATERNION'
        pip.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(normal)

        for polygon in pip.data.polygons:
            polygon.use_smooth = True
