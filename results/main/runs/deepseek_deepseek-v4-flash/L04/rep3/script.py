import bpy
import bmesh  # noqa: F401  (allowed but not required)
import math

# ------------------------------------------------------------
# Clean scene
# ------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ------------------------------------------------------------
# Parameters (all sizes in Blender units)
# ------------------------------------------------------------
# Base – wide cylinder
base_radius  = 1.0
base_height  = 0.4
base_z       = base_height / 2.0          # cylinder center

# Collar – torus (flat ring, axis = Z)
collar_radius = 0.65                      # major radius of torus
collar_tube   = 0.15                      # minor radius
collar_z      = 0.50                      # torus center height

# Body – truncated cone / tapered cylinder
body_radius_bottom = 0.40
body_radius_top    = 0.20
body_height        = 1.00
body_bottom_z      = 0.65                 # cone base sits above collar
body_z             = body_bottom_z + body_height / 2.0

# Head – sphere
head_radius = 0.40
head_z      = 1.65 + head_radius          # sphere bottom touches body top

# ------------------------------------------------------------
# Create all parts
# ------------------------------------------------------------
# Base
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=base_radius,
    depth=base_height,
    cap_fill_type='TRIFAN',
    location=(0.0, 0.0, base_z)
)
base_obj = bpy.context.object
base_obj.name = "Pawn_Base"

# Collar (torus)
bpy.ops.mesh.primitive_torus_add(
    major_segments=32,
    minor_segments=12,
    mode='MAJOR_MINOR',
    major_radius=collar_radius,
    minor_radius=collar_tube,
    location=(0.0, 0.0, collar_z)
)
collar_obj = bpy.context.object
collar_obj.name = "Pawn_Collar"

# Body (truncated cone)
bpy.ops.mesh.primitive_cone_add(
    vertices=32,
    radius1=body_radius_bottom,
    radius2=body_radius_top,
    depth=body_height,
    end_fill_type='TRIFAN',
    location=(0.0, 0.0, body_z)
)
body_obj = bpy.context.object
body_obj.name = "Pawn_Body"

# Head (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=head_radius,
    location=(0.0, 0.0, head_z)
)
head_obj = bpy.context.object
head_obj.name = "Pawn_Head"

# ------------------------------------------------------------
# Join all parts into one object
# ------------------------------------------------------------
bpy.ops.object.select_all(action='DESELECT')
for obj in [base_obj, collar_obj, body_obj, head_obj]:
    obj.select_set(True)

bpy.context.view_layer.objects.active = base_obj
bpy.ops.object.join()

joined_obj = bpy.context.object
joined_obj.name = "ChessPawn"

# Ensure the final object is selected and active
bpy.ops.object.select_all(action='DESELECT')
joined_obj.select_set(True)
bpy.context.view_layer.objects.active = joined_obj
