import math
import bmesh
import bpy
from mathutils import Matrix, Vector

# Clear existing objects
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Create a single mesh for the entire staircase to control poly count and performance
mesh = bpy.data.meshes.new("SpiralStaircaseMesh")
obj = bpy.data.objects.new("SpiralStaircase", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Parameters
num_steps = 24
angle_increment = math.radians(15.0)
height_increment = 0.25

column_radius = 0.4
column_height = num_steps * height_increment + 0.5

step_inner_radius = column_radius
step_outer_radius = 1.8
step_thickness = 0.1
step_width_angle = math.radians(35.0)  # Width of each step in degrees

# -----------------------------------------------------------------
# 1. Central Cylindrical Column
# -----------------------------------------------------------------
column_segments = 24
bmesh.ops.create_cone(
    bm,
    cap_ends=True,
    cap_tris=False,
    segments=column_segments,
    radius1=column_radius,
    radius2=column_radius,
    depth=column_height,
)
# Move column so its base is at Z=0 and center is adjusted
# create_cone centers at origin, so shift up by half height
matrix_col = Matrix.Translation((0, 0, column_height / 2.0))
bmesh.ops.transform(bm, matrix=matrix_col, verts=bm.verts)

# -----------------------------------------------------------------
# 2. Steps
# -----------------------------------------------------------------
# We create a prototype step at the origin (wedge shape) and duplicate/transform it
step_bm = bmesh.new()

# Create a wedge for a single step
step_segments = 6  # smoothness of outer edge
step_verts = []

# Inner arc and outer arc points
for i in range(step_segments + 1):
    t = i / step_segments
    angle = -step_width_angle / 2 + t * step_width_angle

    # Local coordinates for the step
    x_in = step_inner_radius * math.cos(angle)
    y_in = step_inner_radius * math.sin(angle)
    x_out = step_outer_radius * math.cos(angle)
    y_out = step_outer_radius * math.sin(angle)

    # Bottom and top vertices
    v_bottom = step_bm.verts.new((x_in, y_in, 0))
    v_top = step_bm.verts.new((x_in, y_in, step_thickness))
    # Wait, let's build proper faces. It's easier to create a 2D profile and extrude,
    StaticHandler = None


step_bm.free()

# Instead of a prototype sub-bm, let's construct steps directly in the main bmesh
# using a clean loop for precise control over geometry and UVs.

for i in range(num_steps):
    current_angle = i * angle_increment
    current_height = i * height_increment

    # Create step geometry
    # We will build a solid wedge with radial segments
    radial_segments = 4
    step_span = math.radians(45.0)  # Each step covers 45 degrees arc

    verts_bottom = []
    verts_top = []

    for r in range(radial_segments + 1):
        # Angle along the step width
        frac = r / radial_segments
        ang = current_angle - (step_span * 0.5) + (step_span * frac)

        # We want the step to be slightly wider than the rotation step to overlap nicely
        # Actually, standard spiral stairs: step covers e.g. 40-50 deg, rotation is 15 deg.
        # Let's use step_span = radians(40)

        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        # Inner and outer radii
        v_in_b = bm.verts.new(
            (
                step_inner_radius * cos_a,
                step_inner_radius * sin_a,
                current_height,
            )
        )
        v_in_t = bm.verts.new(
            (
                step_inner_radius * cos_a,
                step_inner_radius * sin_a,
                current_height + step_thickness,
            )
        )
        v_out_b = bm.verts.new(
            (
                step_outer_radius * cos_a,
                step_outer_radius * sin_a,
                current_height,
            )
        )
        v_out_t = bm.verts.new(
            (
                step_outer_radius * cos_a,
                step_outer_radius * sin_a,
                current_height + step_thickness,
            )
        )

        # Store for face creation
        # We'll build a grid of faces for this single step block

    # Let's use a simpler, highly robust method for step creation:
    # A step is a prism defined by bottom polygon and extruded up.


# Let's rewrite the step loop with a clean bmesh prism approach:
def create_step(bm, base_angle, height, inner_r, outer_r, thickness):
    span = math.radians(38.0)  # Step angular width
    segs = 4

    bottom_verts = []
    top_verts = []

    for s in range(segs + 1):
        a = base_angle - span / 2 + (span * (s / segs))
        ca, sa = math.cos(a), math.sin(a)
        bottom_verts.append(bm.verts.new((inner_r * ca, inner_r * sa, height)))
        top_verts.append(
            bm.verts.new((inner_r * ca, inner_r * sa, height + thickness))
        )

    # Outer arc
    outer_bottom = []
    outer_top = []
    for s in range(segs + 1):
        a = base_angle - span / 2 + (span * (s / segs))
        ca, sa = math.cos(a), math.sin(a)
        outer_bottom.append(
            bm.verts.new((outer_r * ca, outer_r * sa, height))
        )
        outer_top.append(
            bm.verts.new((outer_r * ca, outer_r * sa, height + thickness))
        )

    # Re-order/combine into a proper grid for bmesh bridge loops or manual face creation
    # To keep code concise and avoid complex index bookkeeping, let's use bmesh primitives
    # or create a generalized wedge via rotation matrices.


# --- Robust Approach: Build Step via Transformation of a Template Wedge ---

# 1. Make a template wedge at origin
wedge_bm = bmesh.new()
# Create a block in local space: X from inner to outer, Y from -width/2 to +width/2, Z from 0 to thickness
r_in = step_inner_radius
r_out = step_outer_radius
thick = step_thickness
span = math.radians(40.0)

# We can just construct the vertices of the wedge directly
seg_count = 4
v_bottoms = []
v_tops = []

for i in range(seg_count + 1):
    fraction = i / seg_count
    angle = -span / 2 + span * fraction
    c, s = math.cos(angle), math.sin(angle)

    v_b1 = wedge_bm.verts.new((r_in * c, r_in * s, 0))
    v_b2 = wedge_bm.verts.new((r_out * c, r_out * s, 0))
    v_t1 = wedge_bm.verts.new((r_in * c, r_in * s, thick))
    v_t2 = wedge_bm.verts.new((r_out * c, r_out * s, thick))

    v_bottoms.append((v_b1, v_b2))
    v_tops.append((v_t1, v_t2))

# Connect vertices into faces for the wedge
wedge_faces = []
# Bottom cap
b_face_verts = [vb[0] for vb in v_bottoms] + [
    vb[1] for vb in reversed(v_bottoms)
]  # wait, simple strip is better:
# Let's just use bmesh operations to build a clean box-like wedge:
wedge_bm.free()

# Let's use Blender's internal primitives for steps: cubes scaled and positioned.
# Even simpler and 100% reliable for face counts:
for i in range(num_steps):
    ang = i * angle_increment
    h = i * height_increment

    # Create a small cube for the step, deform it with a simple matrix or vertex manipulation
    # Or just use bmesh.ops.create_cube and transform it
    cube = bmesh.ops.create_cube(bm, size=1.0)
    verts = cube["verts"]

    # Transform each vertex of the cube into a stepped wedge sector
    # Matrix to position the step: rotate by 'ang', translate outward and upward
    # Instead, let's calculate analytically per vertex:
    bmesh.ops.delete(bm, geom=verts, dt="VERTS")  # Clear that test cube

# Let's write a clean procedural loop that adds geometry directly to `bm`.
for i in range(num_steps):
    ang_center = i * angle_increment
    z_base = i * height_increment

    # Number of radial slices for smooth outer edge
    slices = 4
    d_ang = math.radians(40.0)

    # Build rings of vertices (bottom and top)
    ring_bottom = []
    ring_top = []

    for s in range(slices + 1):
        a = ang_center - (d_ang / 2) + (d_ang * (s / slices))
        ca, sa = math.cos(a), math.sin(a)

        rb = bm.verts.new((column_radius * ca, column_radius * sa, z_base))
        rt = bm.verts.new(
            (column_radius * ca, column_radius * sa, z_base + step_thickness)
        )
        ring_bottom.append(rb)
        ring_top.append(rt)

    outer_bottom = []
    outer_top = []
    for s in range(slices + 1):
        a = ang_center - (d_ang / 2) + (d_ang * (s / slices))
        ca, sa = math.cos(a), math.sin(a)

        rb = bm.verts.new((step_outer_radius * ca, step_outer_radius * sa, z_base))
        rt = bm.verts.new(
            (
                step_outer_radius * ca,
                step_outer_radius * sa,
                z_base + step_thickness,
            )
        )
        outer_bottom.append(rb)
        outer_top.append(rt)

    # Now create faces
    # 1. Bottom face
    bm.faces.new(ring_bottom + list(reversed(outer_bottom)))
    # 2. Top face
    bm.faces.new(list(reversed(ring_top)) + outer_top)

    # 3. Inner side (connect ring_bottom to ring_top along inner radius)
    for s in range(slices):
        bm.faces.new(
            [
                ring_bottom[s],
                ring_bottom[s + 1],
                ring_top[s + 1],
                ring_top[s],
            ]
        )

    # 4. Outer side
    for s in range(slices):
        bm.faces.new(
            [
                outer_bottom[s + 1],
                outer_bottom[s],
                outer_top[s],
                outer_top[s + 1],
            ]
        )

    # 5. Side walls (start and end angles)
    bm.faces.new(
        [ring_bottom[0], outer_bottom[0], outer_top[0], ring_top[0]]
    )
    bm.faces.new(
        [
            outer_bottom[-1],
            ring_bottom[-1],
            ring_top[-1],
            outer_top[-1],
        ]
    )

# -----------------------------------------------------------------
# 3. Helical Handrail & Balusters
# -----------------------------------------------------------------
# Generate vertical balusters on the outer edge of each step
baluster_radius = 0.03
rail_radius = 0.04
rail_height_offset = 1.0

handrail_points = []

for i in range(num_steps):
    ang_center = i * angle_increment
    z_base = i * height_increment + step_thickness

    # Position baluster at the outer-middle edge of the step
    a = ang_center
    ca, sa = math.cos(a), math.sin(a)
    bx = (step_outer_radius - 0.1) * ca
    by = (step_outer_radius - 0.1) * sa

    # Create a small cylinder for the baluster
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=6,
        radius1=baluster_radius,
        radius2=baluster_radius,
        depth=rail_height_offset,
    )
    # Move baluster into position
    # Cone is centered at origin, so shift up by half height + base z
    mat_bal = Matrix.Translation(
        (bx, by, z_base + rail_height_offset / 2.0)
    )
    # Collect newly added verts (we can transform all selected or track them,
    # but a simpler way is to transform the whole bm state or just build a helper function).
    # Since we want to transform *only* the new baluster verts, let's tag them or use a separate bmesh and merge.

# Cleaner approach for balusters and handrail: use bmesh to add them directly with pre-applied transforms
for i in range(num_steps):
    ang_center = i * angle_increment
    z_base = i * height_increment + step_thickness

    a = ang_center
    bx = (step_outer_radius - 0.1) * math.cos(a)
    by = (step_outer_radius - 0.1) * math.sin(a)
    bz = z_base + rail_height_offset / 2.0

    # Add a primitive cylinder for baluster
    ret = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=6,
        radius1=baluster_radius,
        radius2=baluster_radius,
        depth=rail_height_offset,
    )
    bmesh.ops.transform(
        bm,
        matrix=Matrix.Translation((bx, by, bz)),
        verts=ret["verts"],
    )

    # Collect points for the continuous helical handrail curve
    handrail_points.append(
        Vector((bx, by, z_base + rail_height_offset))
    )

# Build the helical handrail smoothly connecting the points
# We can sweep a small circle along the points, or build a smooth curve of cylinders/segments.
# Let's connect consecutive handrail points with small cylinder segments.
for i in range(len(handrail_points) - 1):
    p1 = handrail_points[i]
    p2 = handrail_points[i + 1]

    # Vector from p1 to p2
    dir_vec = p2 - p1
    length = dir_vec.length

    # Create a cylinder aligned along Z, then rotate and translate it to match dir_vec
    ret = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=6,
        radius1=rail_radius,
        radius2=rail_radius,
        depth=length,
    )

    # Calculate rotation from Z-axis (0, 0, 1) to dir_vec
    z_axis = Vector((0, 0, 1))
    rot_quat = z_axis.rotation_difference(dir_vec)
    rot_mat = rot_quat.to_matrix().to_4x4()

    # Midpoint translation
    mid_point = p1 + dir_vec * 0.5
    trans_mat = Matrix.Translation(mid_point)

    # Combine matrices: Translate * Rotate
    final_mat = trans_mat @ rot_mat
    bmesh.ops.transform(bm, matrix=final_mat, verts=ret["verts"])

# Finalize mesh update
bm.to_mesh(mesh)
bm.free()

# Enable smooth shading across the generated mesh for a clean appearance
for f in mesh.polygons:
    f.use_smooth = True

# Ensure correct normals
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
