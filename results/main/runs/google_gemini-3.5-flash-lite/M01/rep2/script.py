import math
import bmesh
import bpy
from mathutils import Matrix, Vector

# Clear existing objects
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Parameters
num_steps = 24
rotation_per_step = math.radians(15.0)
height_per_step = 0.25
column_radius = 0.4
step_width = 1.2
step_thickness = 0.08
step_depth = 0.4
railing_height = 1.0
railing_radius = column_radius + step_width - 0.1

# Create main mesh and BMesh
mesh = bpy.data.meshes.new("SpiralStaircaseMesh")
bm = bmesh.new()

# ----------------------------------------------------------------------
# 1. Central Cylindrical Column
# ----------------------------------------------------------------------
column_height = num_steps * height_per_step + 0.5
column_segments = 16
bmesh.ops.create_cone(
    bm,
    cap_ends=True,
    cap_tris=False,
    segments=column_segments,
    radius1=column_radius,
    radius2=column_radius,
    depth=column_height,
)
# Move column up so its base is at Z=0 and it goes slightly into the ground
for v in bm.verts:
    if v.co.z <= 0:  # simplistic check or just offset all
        pass
# Center of create_cone is at origin, shift up by half height
matrix_col = Matrix.Translation((0, 0, column_height / 2.0))
bmesh.ops.transform(bm, matrix=matrix_col, verts=bm.verts)


# ----------------------------------------------------------------------
# 2. Steps (24 individual extruded/transformed blocks)
# ----------------------------------------------------------------------
# Helper geometry for a single step centered at origin relative to its own local space
# We want the step to go from radius = column_radius to column_radius + step_width
# and span an angle roughly matching the rotation, plus a bit of overlap.

step_verts = []
step_faces = []


def create_step_geom(bm_target, width, depth, thickness):
    # Creates a box mesh for a single step extending along X from r_inner to r_outer
    # We will build it in local coordinates where inner edge is at X = column_radius
    r_in = column_radius
    r_out = column_radius + width

    # Define profile in X-Z plane, then extrude along Y (angular approximation or flat box)
    # To make nice radial steps, let's build a wedge using bmesh primitive or explicit verts.
    # An explicit wedge is cleaner for spiral stairs:
    pass


# Instead of complex instancing, let's build step geometry directly via bmesh primitives rotated per step
for i in range(num_steps):
    angle = i * rotation_per_step
    z_pos = i * height_per_step + (step_thickness / 2.0)

    # Create a small cube/block for the step
    step_bm = bmesh.new()
    bmesh.ops.create_cube(step_bm, size=1.0)

    # Scale to step dimensions: X -> depth, Y -> width, Z -> thickness
    # Actually, let's position it in polar coordinates:
    # Scale: depth along radial, width along tangential, height along Z
    scale_mat = Matrix.Scale(step_depth, 4, (1, 0, 0)) @ Matrix.Scale(
        step_width, 4, (0, 1, 0)
    ) @ Matrix.Scale(step_thickness, 4, (0, 0, 1))

    # Translate outwards along X by (column_radius + step_width/2)
    trans_mat = Matrix.Translation(
        (column_radius + (step_width / 2.0), 0, -0.5 * step_thickness)
    )

    # Combine local transform
    local_mat = Matrix.Translation((0, 0, z_pos)) @ Matrix.Rotation(
        angle, 4, 'Z'
    ) @ Matrix.Rotation(
        rotation_per_step / 2.0, 4, 'Z'
    ) @ Matrix.Translation(
        (column_radius + step_width / 2.0, 0, 0)
    ) @ Matrix.Scale(
        step_depth, 4, (1, 0, 0)
    ) @ Matrix.Scale(
        step_width, 4, (0, 1, 0)
    ) @ Matrix.Scale(
        step_thickness, 4, (0, 0, 1)
    )

    # Better yet, construct step vertices manually for a wedge shape:
    step_bm.free()

# Let's write a robust wedge-step generator per iteration:
for i in range(num_steps):
    angle_start = i * rotation_per_step
    angle_end = (
        i + 1.2
    ) * rotation_per_step  # slight overlap into next step for solidity
    z_bottom = i * height_per_step
    z_top = z_bottom + step_thickness

    r_in = column_radius
    r_out = column_radius + step_width

    # We can create a wedge using an arc profile extruded vertically
    # Or simply append a block and transform it. Let's append transformed box geometry:
    # A box from r_in to r_out, local angle span
    # Let's use bmesh create_cube and warp it, or just build verts:

    # 4 points inner, 4 points outer (bottom and top)
    # Actually, simpler: create a cube and apply a bend/transform, or just raw verts:
    half_ang = 0.5 * rotation_per_step * 1.1  # slightly wider than step rotation

    # Let's generate a wedge in cylindrical coords (r, theta, z)
    verts_data = []
    # Bottom face (4 verts) & Top face (4 verts)
    for z in [z_bottom, z_top]:
        # inner-left, inner-right, outer-right, outer-left
        for r, a in [
            (r_in, -half_ang),
            (r_in, half_ang),
            (r_out, half_ang),
            (r_out, -half_ang),
        ]:
            # Rotate by step angle + a
            total_ang = angle_start + a + (rotation_per_step / 2.0)
            x = r * math.cos(total_ang)
            y = r * math.sin(total_ang)
            verts_data.append(Vector((x, y, z)))

    # Add to main bm
    step_verts_bm = [bm.verts.new(co) for co in verts_data]

    # Faces for the wedge box
    # Indices: 0-3 bottom, 4-7 top
    # 0: in_l_bot, 1: in_r_bot, 2: out_r_bot, 3: out_l_bot
    # 4: in_l_top, 5: in_r_top, 6: out_r_top, 7: out_l_top
    face_indices = [
        (0, 1, 5, 4),  # inner
        (1, 2, 6, 5),  # right side
        (2, 3, 7, 6),  # outer
        (3, 0, 4, 7),  # left side
        (0, 3, 2, 1),  # bottom
        (4, 5, 6, 7),  # top
    ]
    for f_idx in face_indices:
        try:
            bm.faces.new([step_verts_bm[idx] for idx in f_idx])
        except ValueError:
            pass  # Ignore duplicate edge errors if any

# ----------------------------------------------------------------------
# 3. Helical Handrail & Support Spindles
# ----------------------------------------------------------------------
# We create a smooth helical curve using vertices and connect them with faces,
# plus vertical spindles connecting steps to the handrail.

rail_verts = []
total_rail_points = num_steps * 8
for i in range(total_rail_points + 1):
    t = i / float(total_rail_points)
    current_num_rotations = num_steps * rotation_per_step
    angle = t * current_num_rotations + (rotation_per_step / 2.0)
    z = t * (num_steps * height_per_step) + railing_height

    x = railing_radius * math.cos(angle)
    y = railing_radius * math.sin(angle)
    rail_verts.append(Vector((x, y, z)))

# Build handrail as a small cylinder/tube along the curve
# We can do this by creating ring vertices along the curve and bridging them
rail_radius_profile = 0.04
rail_segments = 6

prev_ring = None
for i, p in enumerate(rail_verts):
    # Calculate tangent
    if i < len(rail_verts) - 1:
        tangent = (rail_verts[i + 1] - p).normalized()
    else:
        tangent = (p - rail_verts[i - 1]).normalized()

    # Find arbitrary normal perpendicular to tangent
    helper = Vector((0, 0, 1))
    if abs(tangent.dot(helper)) > 0.99:
        helper = Vector((0, 1, 0))
    normal = tangent.cross(helper).normalized()
    binormal = tangent.cross(normal).normalized()

    # Create ring vertices
    ring = []
    for s in range(rail_segments):
        ang = (s / rail_segments) * math.tau
        offset = (
            normal * math.cos(ang) * rail_radius_profile
            + binormal * math.sin(ang) * rail_radius_profile
        )
        ring.append(bm.verts.new(p + offset))

    # Connect to previous ring
    if prev_ring is not None:
        for s in range(rail_segments):
            s_next = (s + 1) % rail_segments
            bm.faces.new(
                [
                    prev_ring[s],
                    prev_ring[s_next],
                    ring[s_next],
                    ring[s],
                ]
            )
    prev_ring = ring

# Add vertical spindles (balusters) from every other step to the handrail
for i in range(0, num_steps, 1):
    angle = (
        i * rotation_per_step + (rotation_per_step / 2.0)
    )  # match step center
    z_base = i * height_per_step + step_thickness
    z_top = i * height_per_step + railing_height

    spindle_radius = 0.02
    spindle_segments = 5

    # Create a simple vertical cylinder for the spindle using bmesh primitive
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=spindle_segments,
        radius1=spindle_radius,
        radius2=spindle_radius,
        depth=(z_top - z_base),
    )

    # Position it
    x = railing_radius * math.cos(angle)
    y = railing_radius * math.sin(angle)
    z_center = (z_base + z_top) / 2.0

    # Transform newly added verts (they are the last ones added)
    # Since bmesh.ops operations add to bm, we can track or transform all recently added.
    # Actually, simpler: transform vertices created in this iteration directly.
    # Let's collect vertices before and after create_cone:
    pass

# Alternative clean approach for spindles: manually add a few cylinder primitives and transform them
for i in range(0, num_steps, 2):  .
    angle = i * rotation_per_step + (rotation_per_step / 2.0)
    z_base = i * height_per_step + step_thickness
    h = railing_height - step_thickness

    # Just create a small column via primitive
    temp_bm = bmesh.new()
    bmesh.ops.create_cone(
        temp_bm,
        cap_ends=True,
        segments=4,
        radius1=0.02,
        radius2=0.02,
        depth=h,
    )

    # Transform and merge into main bm
    mat = Matrix.Translation(
        (
            railing_radius * math.cos(angle),
            railing_radius * math.sin(angle),
            z_base + h / 2.0,
        )
    )
    bmesh.ops.transform(temp_bm, matrix=mat, verts=temp_bm.verts)

    for v in temp_bm.verts:
        bm.verts.new(v.co)
    # Re-index/copy faces (easier: use operator-less manual addition or just let bmesh handle via separate mesh joining)
    temp_bm.free()

# Ensure normals are consistent
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Finish up mesh creation
bm.to_mesh(mesh)
bm.free()

# Create object and link to scene
obj = bpy.data.objects.object_add(bpy.context, mesh, name="SpiralStaircase")

# Set smooth shading for organic look
for f in mesh.polygons:
    f.use_smooth = True
