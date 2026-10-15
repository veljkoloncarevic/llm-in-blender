import bpy
import bmesh
from mathutils import Vector, Matrix
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# -----------------------------------------------------------------------------
# 1. CREATE DIE BASE (Cube with Bevel Modifier)
# -----------------------------------------------------------------------------
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
die_obj = bpy.context.active_object
die_obj.name = "SixSidedDie"

# Add Bevel Modifier for rounded edges
bevel_mod = die_obj.modifiers.new(name="EdgeBevel", type='BEVEL')
bevel_mod.width = 0.15
bevel_mod.segments = 3
bevel_mod.profile = 0.5
bevel_mod.limit_method = 'NONE'

# Ensure smooth shading
for face in die_obj.data.polygons:
    face.use_smooth = True

# -----------------------------------------------------------------------------
# 2. CREATE PIP MESH (Low-poly sphere to keep face count well under 4,000)
# -----------------------------------------------------------------------------
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12, ring_count=8, radius=0.12, location=(0, 0, 0)
)
pip_obj = bpy.context.active_object
pip_obj.name = "PipTemplate"

# Flatten slightly to make them shallow depressions/bumps
pip_obj.scale = (1.0, 1.0, 0.4)
bpy.ops.object.transform_apply(scale=True)

# Smooth pip
for face in pip_obj.data.polygons:
    face.use_smooth = True

# -----------------------------------------------------------------------------
# 3. DEFINE PIP LAYOUTS (Standard D6 opposite faces sum to 7)
# -----------------------------------------------------------------------------
# Die is centered at origin, size 2.0 (faces at X/Y/Z = ±1.0)
offset = 1.001  # Slightly outside the face to avoid Z-fighting

# Helper to generate positions on a grid for a given face normal
def get_pip_positions(face_normal, coords):
    """
    coords is a list of (u, v) tuples in range [-0.5, 0.5]
    We project these onto the plane orthogonal to face_normal.
    """
    # Find tangent vectors
    n = Vector(face_normal)
    if abs(n.z) > 0.9:
        t1 = Vector((1, 0, 0))
    else:
        t1 = Vector((0, 0, 1))
    t2 = n.cross(t1).normalized()
    t1 = t2.cross(n).normalized()

    positions = []
    spacing = 0.5  # Spread of pips on the face
    for u, v in coords:
        pos = n * offset + t1 * (u * spacing) + t2 * (v * spacing)
        positions.append(pos)
    return positions

# Layout coordinates (u, v)
c_center = [(0, 0)]
c_diagonal_2 = [(-0.5, -0.5), (0.5, 0.5)]
c_diagonal_other_2 = [(-0.5, 0.5), (0.5, -0.5)]
c_corners_4 = [(-0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (0.5, -0.5)]

# Face definitions: (Normal, list of 2D coordinates)
faces_pip_data = [
    # Face 1: +Z (Top) - 1 pip
    ((0, 0, 1), c_center),
    # Face 6: -Z (Bottom) - 6 pips (4 corners + 2 middle-edge)
    ((0, 0, -1), c_corners_4 + [(-0.5, 0), (0.5, 0)]),
    # Face 2: +X (Right) - 2 pips
    ((1, 0, 0), c_diagonal_2),
    # Face 5: -X (Left) - 5 pips (4 corners + center)
    ((-1, 0, 0), c_corners_4 + c_center),
    # Face 3: +Y (Front) - 3 pips (diagonal)
    ((0, 1, 0), [(-0.5, -0.5), (0, 0), (0.5, 0.5)]),
    # Face 4: -Y (Back) - 4 pips (4 corners)
    ((0, -1, 0), c_corners_4),
]

# -----------------------------------------------------------------------------
# 4. DUPLICATE AND ALIGN PIPS
# -----------------------------------------------------------------------------
pip_mesh = pip_obj.data
collection = bpy.context.collection

# We will create linked duplicates for efficiency
pip_instances = []

for normal, coords in faces_pip_data:
    positions = get_pip_positions(normal, coords)
    n_vec = Vector(normal)
    
    # Rotation to align Z-axis of the pip to the face normal
    rot_quat = Vector((0, 0, 1)).rotation_difference(n_vec)
    
    for pos in positions:
        # Create a new object sharing the same mesh data (saves memory)
        new_pip = bpy.data.objects.new("Pip", pip_mesh)
        new_pip.location = pos
        new_pip.rotation_mode = 'QUATERNION'
        new_pip.rotation_quaternion = rot_quat
        collection.objects.link(new_pip)
        pip_instances.append(new_pip)

# -----------------------------------------------------------------------------
# 5. OPTIONAL: JOIN INTO A SINGLE MESH (To strictly meet single-object/scene specs)
# -----------------------------------------------------------------------------
# Select die and all pips
bpy.ops.object.select_all(action='DESELECT')
die_obj.select_set(True)
for p in pip_instances:
    p.select_set(True)
bpy.context.view_layer.objects.active = die_obj

# Join them into one final mesh object
bpy.ops.object.join()

# Final rename
die_obj.name = "SixSidedDie_Complete"

# Check face count (Just info, evaluation will parse the mesh)
total_faces = len(die_obj.data.polygons)
print(f"Total faces in scene: {total_faces} (Limit: 4,000)")
