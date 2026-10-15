import bpy
import bmesh

# Switch to Object Mode if necessary
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Wide cylinder base ---
bpy.ops.mesh.primitive_cylinder_add(
    vertices=24,
    radius=1.0,
    depth=0.3,
    location=(0.0, 0.0, 0.15)
)
base = bpy.context.object
base.name = "Pawn_Base"

# --- Torus collar ---
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.15,
    major_segments=24,
    minor_segments=12,
    location=(0.0, 0.0, 0.45)
)
collar = bpy.context.object
collar.name = "Pawn_Collar"

# --- Tapered body (cylinder edited into a frustum) ---
bpy.ops.mesh.primitive_cylinder_add(
    vertices=24,
    radius=0.5,
    depth=1.0,
    location=(0.0, 0.0, 1.1)
)
body = bpy.context.object
body.name = "Pawn_Body"

# Enter edit mode and scale the top ring down
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(body.data)
max_z = max(v.co.z for v in bm.verts)
for v in bm.verts:
    if v.co.z > max_z - 0.001:
        v.co.x *= 0.6
        v.co.y *= 0.6
bmesh.update_edit_mesh(body.data)
bpy.ops.object.mode_set(mode='OBJECT')

# --- Sphere head ---
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=24,
    ring_count=12,
    radius=0.4,
    location=(0.0, 0.0, 1.85)
)
head = bpy.context.object
head.name = "Pawn_Head"
