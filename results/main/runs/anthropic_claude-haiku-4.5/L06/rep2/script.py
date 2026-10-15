import bpy
import bmesh
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the main die cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
die_cube = bpy.context.active_object
die_cube.name = "Die"

# Add bevel modifier with 3 segments
bevel_mod = die_cube.modifiers.new(name="Bevel", type='BEVEL')
bevel_mod.width = 0.15
bevel_mod.segments = 3

# Define pip positions for each face (1-6 pips)
# Faces are: +X, -X, +Y, -Y, +Z, -Z
pip_configs = {
    # Face +Z (top) - 1 pip at center
    'Z+': [(0, 0, 1.0)],
    # Face -Z (bottom) - 6 pips
    'Z-': [(-0.6, -0.6, -1.0), (-0.6, 0.6, -1.0), (0.6, -0.6, -1.0), 
           (0.6, 0.6, -1.0), (0, -0.6, -1.0), (0, 0.6, -1.0)],
    # Face +X (right) - 3 pips
    'X+': [(-0.4, -0.4, 1.0), (0, 0, 1.0), (0.4, 0.4, 1.0)],
    # Face -X (left) - 4 pips
    'X-': [(-0.5, -0.5, -1.0), (-0.5, 0.5, -1.0), (0.5, -0.5, -1.0), (0.5, 0.5, -1.0)],
    # Face +Y (front) - 2 pips
    'Y+': [(-0.5, 0, 1.0), (0.5, 0, 1.0)],
    # Face -Y (back) - 5 pips
    'Y-': [(-0.6, 0, -1.0), (0.6, 0, -1.0), (-0.3, -0.5, -1.0), 
           (0.3, -0.5, -1.0), (0, 0.5, -1.0)]
}

# Face transformations (position, rotation axis, rotation amount)
face_transforms = {
    'Z+': (Vector((0, 0, 1.05)), Vector((0, 0, 1)), 0),
    'Z-': (Vector((0, 0, -1.05)), Vector((0, 0, 1)), 0),
    'X+': (Vector((1.05, 0, 0)), Vector((0, 1, 0)), 1.5708),  # 90 degrees
    'X-': (Vector((-1.05, 0, 0)), Vector((0, 1, 0)), 1.5708),
    'Y+': (Vector((0, 1.05, 0)), Vector((1, 0, 0)), 1.5708),
    'Y-': (Vector((0, -1.05, 0)), Vector((1, 0, 0)), 1.5708),
}

pip_count = 0

# Create pips for each face
for face_key, pips in pip_configs.items():
    face_pos, rot_axis, rot_angle = face_transforms[face_key]
    
    for pip_local_pos in pips:
        # Create small cylinder for pip
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.12,
            depth=0.15,
            vertices=8,
            location=face_pos
        )
        pip = bpy.context.active_object
        pip.name = f"Pip_{pip_count}"
        pip_count += 1
        
        # Rotate pip to face direction
        pip.rotation_axis_angle = (rot_angle, rot_axis[0], rot_axis[1], rot_axis[2])
        
        # Position pip on face using local coordinates
        # Transform local pip position to world space
        local_offset = Vector(pip_local_pos)
        
        # Rotate the local offset
        if face_key == 'X+':
            world_offset = Vector((0, local_offset[1], local_offset[2]))
        elif face_key == 'X-':
            world_offset = Vector((0, local_offset[1], local_offset[2]))
        elif face_key == 'Y+':
            world_offset = Vector((local_offset[0], 0, local_offset[2]))
        elif face_key == 'Y-':
            world_offset = Vector((local_offset[0], 0, local_offset[2]))
        else:  # Z+ or Z-
            world_offset = Vector((local_offset[0], local_offset[1], 0))
        
        pip.location += world_offset
        
        # Scale down the pip slightly
        pip.scale = (0.5, 0.5, 0.3)

# Set viewport shading for better visibility
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

print("Six-sided die created successfully with rounded edges and pips!")
