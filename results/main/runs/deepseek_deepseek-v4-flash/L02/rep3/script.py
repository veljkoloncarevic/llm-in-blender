import bpy
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Snowman body ---

# Bottom sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16, ring_count=8, radius=1.0, location=(0, 0, 0)
)
bpy.context.active_object.name = "Snowman_Bottom"

# Middle sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16, ring_count=8, radius=0.7, location=(0, 0, 1.7)
)
bpy.context.active_object.name = "Snowman_Middle"

# Head
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=16, ring_count=8, radius=0.5, location=(0, 0, 2.9)
)
bpy.context.active_object.name = "Snowman_Head"

# --- Eyes ---
eye_radius = 0.08
eye_offset_x = 0.15
eye_offset_z = 0.1
eye_y = 0.45  # slightly forward from head center

for side in (-1, 1):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=4, radius=eye_radius,
        location=(side * eye_offset_x, eye_y, 2.9 + eye_offset_z)
    )
    eye = bpy.context.active_object
    eye.name = "Snowman_Eye_Left" if side < 0 else "Snowman_Eye_Right"

# --- Nose (carrot) ---
bpy.ops.mesh.primitive_cone_add(
    vertices=8,
    radius1=0.1,
    radius2=0.0,
    depth=0.5,
    end_fill_type='NGON',
    location=(0, 0.5, 2.9)  # base at head surface
)
nose = bpy.context.active_object
nose.name = "Snowman_Nose"
nose.rotation_euler = (-math.pi / 2, 0, 0)  # rotate cone to point +Y
