import math
import bmesh
import bpy
from mathutils import Vector

# 1. Clear existing objects
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# 2. Create the base die cube
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))
die = bpy.active_object
die.name = "Die"

# Add Bevel modifier for rounded edges
bevel = die.modifiers.new(name="Bevel", type="BEVEL")
bevel.width = 0.12
bevel.segments = 3
bevel.limit_method = "NONE"

# Apply transforms and modifiers to get clean geometry for boolean operations
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.modifier_apply(modifier="Bevel")

# 3. Model pips as shallow cylinders (capsules/discs) and boolean cut them
# Standard die layout opposite faces sum to 7: (1-6, 2-5, 3-4)
# Cube size is 2.0, so faces are at X/Y/Z = +/- 1.0
pip_depth = 0.08
pip_radius = 0.16

# Face configurations: coordinate offset, scale, and pip local 2D positions
# Each face lies on a plane at 1.0 or -1.0 along an axis.
# We define pip layouts in 2D relative to the face center.
d = 1.001  # Slightly outside the surface to ensure clean boolean intersection
r = 0.45  # Offset for corner pips
m = 0.00  # Middle pip

layouts = {
    # Face 1: Center (X = 1)
    1: {"normal": (1, 0, 0), "pips": [(m, m)]},
    # Face 6: Six pips in two columns of three (X = -1)
    6: {
        "normal": (-1, 0, 0),
        "pips": [(-r, -r), (-r, m), (-r, r), (r, -r), (r, m), (r, r)],
    },
    # Face 2: Two pips diagonal (Y = 1)
    2: {"normal": (0, 1, 0), "pips": [(-r, -r), (r, r)]},
    # Face 5: Five pips (Y = -1)
    5: {"normal": (0, -1, 0), "pips": [(-r, -r), (-r, r), (m, m), (r, -r), (r, r)]},
    # Face 3: Three pips diagonal (Z = 1)
    3: {"normal": (0, 0, 1), "pips": [(-r, -r), (m, m), (r, r)]},
    # Face 4: Four pips square (Z = -1)
    4: {"normal": (0, 0, -1), "pips": [(-r, -r), (-r, r), (r, -r), (r, r)]},
}

# Collect all pip cutters into a collection, then union them and boolean difference from die
cutters = []

for face_num, data in layouts.items():
    normal = Vector(data["normal"])

    # Determine tangent and bitangent vectors for the face plane
    if abs(normal.z) > 0.9:
        tangent = Vector((1, 0, 0))
        bitangent = Vector((0, 1, 0))
    elif abs(normal.x) > 0.9:
        tangent = Vector((0, 1, 0))
        bitangent = Vector((0, 0, 1))
    else:
        tangent = Vector((1, 0, 0))
        bitangent = Vector((0, 0, 1))

    face_center = normal * 1.0

    for pip_pos in data["pips"]:
        # Calculate 3D position for the pip
        pos = face_center + tangent * pip_pos[0] + bitangent * pip_pos[1]

        # Create a shallow cylinder (disc) for the pip
        # Using low-ish vertices (16) to keep face count well under 4,000
        bpy.ops.mesh.primitive_cylinder_add(
            radius=pip_radius,
            depth=pip_depth * 2,
            vertices=16,
            location=pos + normal * (pip_depth * 0.5),
        )
        cutter = bpy.active_object

        # Orient cutter along face normal
        # Cylinder default orientation is along Z. Rotate if needed.
        if abs(normal.z) < 0.9:
            rot_axis = normal.cross(Vector((0, 0, 1))).normalized()
            rot_angle = math.acos(normal.dot(Vector((0, 0, 1))))
            cutter.rotation_euler = rot_axis * rot_angle
            bpy.ops.object.transform_apply(rotation=True)

        cutters.append(cutter)

# Join all cutters into a single mesh object for efficient boolean processing
bpy.ops.object.select_all(action="DESELECT")
for c in cutters:
    c.select_set(True)
bpy.context.view_layer.objects.active = cutters[0]
bpy.ops.object.join()
pip_cluster = bpy.active_object
pip_cluster.name = "PipCutters"

# Apply Boolean Difference modifier to the die
bool_mod = die.modifiers.new(name="PipBoolean", type="BOOLEAN")
bool_mod.operation = "DIFFERENCE"
bool_mod.object = pip_cluster
bool_mod.solver = "EXACT"

# Apply the boolean modifier
bpy.context.view_layer.objects.active = die
bpy.ops.object.modifier_apply(modifier="PipBoolean")

# Delete the pip cutters object
bpy.data.objects.remove(pip_cluster, do_unlink=True)

# 4. Final Cleanup & Shading
bpy.ops.object.select_all(action="DESELECT")
die.select_set(True)
bpy.context.view_layer.objects.active = die

# Shade smooth with auto smooth for clean low-poly look
bpy.ops.object.shade_smooth()
die.data.use_auto_smooth = True
die.data.auto_smooth_angle = math.radians(35)
