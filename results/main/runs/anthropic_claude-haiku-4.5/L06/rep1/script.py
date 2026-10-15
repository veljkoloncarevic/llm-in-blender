import bpy
import bmesh
from mathutils import Vector
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the main die cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
die = bpy.context.active_object
die.name = "Die"

# Add Bevel modifier with 3 segments
bevel = die.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.15
bevel.segments = 3
bevel.affect = 'EDGES'

# Define pip positions for each face (face normal direction, local positions on face)
# Face layout: +X, -X, +Y, -Y, +Z, -Z corresponding to pips 1,2,3,4,5,6
pip_configs = {
    # Face +X (1 pip - center)
    (1, 0, 0): [(0, 0)],
    # Face -X (2 pips - diagonal)
    (-1, 0, 0): [(-0.6, -0.6), (0.6, 0.6)],
    # Face +Y (3 pips - diagonal line)
    (0, 1, 0): [(-0.6, -0.6), (0, 0), (0.6, 0.6)],
    # Face -Y (4 pips - corners)
    (0, -1, 0): [(-0.6, -0.6), (-0.6, 0.6), (0.6, -0.6), (0.6, 0.6)],
    # Face +Z (5 pips - X pattern)
    (0, 0, 1): [(-0.6, -0.6), (-0.6, 0.6), (0, 0), (0.6, -0.6), (0.6, 0.6)],
    # Face -Z (6 pips - 2x3 grid)
    (0, 0, -1): [(-0.6, -0.6), (-0.6, 0), (-0.6, 0.6), (0.6, -0.6), (0.6, 0), (0.6, 0.6)]
}

pip_radius = 0.15
pip_height = 0.1

# Create pips for each face
for face_normal, positions in pip_configs.items():
    face_x = Vector(face_normal)
    
    # Determine local coordinate system for the face
    if abs(face_normal[0]) > 0.5:  # X-facing
        face_u = Vector((0, 1, 0))
        face_v = Vector((0, 0, 1))
    elif abs(face_normal[1]) > 0.5:  # Y-facing
        face_u = Vector((1, 0, 0))
        face_v = Vector((0, 0, 1))
    else:  # Z-facing
        face_u = Vector((1, 0, 0))
        face_v = Vector((0, 1, 0))
    
    for u, v in positions:
        # Position on face surface
        face_center = face_x * 1.0
        local_pos = face_u * u + face_v * v
        pip_pos = face_center + local_pos
        
        # Create shallow cylinder for pip
        bpy.ops.mesh.primitive_cylinder_add(
            radius=pip_radius,
            depth=pip_height,
            vertices=6,
            location=tuple(pip_pos)
        )
        pip = bpy.context.active_object
        pip.name = f"Pip_{face_normal}_{u}_{v}"
        
        # Rotate cylinder to face outward
        rot_axis = face_u.cross(face_v)
        if rot_axis.length > 0.01:
            rot_axis.normalize()
            angle = math.acos(max(-1, min(1, face_x.dot(Vector((0, 0, 1))))))
            if angle > 0.01:
                pip.rotation_axis_angle = (angle, rot_axis.x, rot_axis.y, rot_axis.z)

# Join all objects
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = die
bpy.ops.object.join()

# Final object is the die with pips
die.name = "Die_Complete"
