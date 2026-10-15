import bpy
import bmesh
import math
from mathutils import Matrix, Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_oval_link_mesh(major_radius=1.0, minor_radius=0.35, length=2.0, segments_path=32, segments_tube=16):
    """
    Creates a procedural oval (stadium-shaped) link mesh using bmesh.
    An oval link consists of two straight segments and two semi-circular ends.
    """
    bm = bmesh.new()
    
    # We construct the link in the XY plane, elongated along the X axis.
    # Total length along X is `length`. The straight parts go from -half_len to +half_len.
    # The semi-circles are at the ends.
    half_len = max(0.0, (length - (2.0 * major_radius)) / 2.0)
    
    # Generate profile circle (tube cross-section) in the YZ plane
    profile_verts = []
    for i in range(segments_tube):
        angle = 2.0 * math.pi * i / segments_tube
        y = minor_radius * math.cos(angle)
        z = minor_radius * math.sin(angle)
        profile_verts.append((0.0, y, z))
        
    # Build path points for the oval center
    # Path goes: right straight -> right arc -> left straight -> left arc
    path_points = []
    
    # Resolution for the curved ends
    arc_segments = max(4, segments_path // 4)
    
    # Right straight (from -half_len to +half_len along X, at y = major_radius)
    # Actually, let's trace a complete loop:
    # 1. Right end semicircle (from -pi/2 to pi/2 around center (+half_len, 0, 0))
    # 2. Top straight (from +half_len to -half_len at y = major_radius)
    # 3. Left end semicircle (from pi/2 to 3pi/2 around center (-half_len, 0, 0))
    # 4. Bottom straight (from -half_len to +half_len at y = -major_radius)
    
    total_path_segs = segments_path
    segs_per_quarter = total_path_segs // 4
    
    centers = []
    
    # To cleanly generate, let's parameterize the 2D loop in XY
    # Perimeter parts:
    # Right semicircle
    for i in range(segs_per_quarter):
        theta = -math.pi/2.0 + (math.pi * i / segs_per_quarter)
        centers.append(Vector((half_len + major_radius * math.cos(theta), major_radius * math.sin(theta), 0.0)))
        
    # Top straight
    for i in range(segs_per_quarter):
        t = i / segs_per_quarter
        x = half_len * (1.0 - t) + (-half_len) * t
        centers.append(Vector((x, major_radius, 0.0)))
        
    # Left semicircle
    for i in range(segs_per_quarter):
        theta = math.pi/2.0 + (math.pi * i / segs_per_quarter)
        centers.append(Vector((-half_len + major_radius * math.cos(theta), major_radius * math.sin(theta), 0.0)))
        
    # Bottom straight
    for i in range(segs_per_quarter):
        t = i / segs_per_quarter
        x = -half_len * (1.0 - t) + half_len * t
        centers.append(Vector((x, -major_radius, 0.0)))

    num_path = len(centers)
    
    # Construct rings along the path
    grid_verts = []
    for p_idx, center in enumerate(centers):
        # Determine tangent to orient the profile ring
        next_center = centers[(p_idx + 1) % num_path]
        prev_center = centers[(p_idx - 1) % num_path]
        tangent = (next_center - prev_center).normalized()
        
        # Up vector for alignment
        # In XY plane, normal of the loop is Z (0,0,1).
        # So radial vector in plane is tangent.cross(Z).
        # Let's define local frame:
        z_axis = Vector((0, 0, 1))
        x_axis = tangent
        y_axis = z_axis.cross(x_axis).normalized()
        
        ring_verts = []
        for v_pos in profile_verts:
            # v_pos is (0, y, z) relative to tube center
            # Map y to y_axis, z to z_axis (or rather, radial and thickness)
            # Profile is in YZ, we want tube cross-section orthogonal to tangent.
            # Let's build matrix from axes:
            # Ring local Y -> y_axis, Ring local Z -> z_axis
            loc_pos = center + y_axis * v_pos[1] + z_axis * v_pos[2]
            v = bm.verts.new(loc_pos)
            ring_verts.append(v)
        grid_verts.append(ring_verts)
        
    # Connect rings with faces
    for i in range(num_path):
        next_i = (i + 1) % num_path
        r1 = grid_verts[i]
        r2 = grid_verts[next_i]
        n_tube = len(profile_verts)
        for j in range(n_tube):
            next_j = (j + 1) % n_tube
            v1 = r1[j]
            v2 = r1[next_j]
            v3 = r2[next_j]
            v4 = r2[j]
            bm.faces.new((v1, v2, v3, v4))
            
    bm.normal_update()
    return bm

# Parameters for the chain
num_links = 12
spacing = 2.4  # Distance between link centers along the chain axis (Z axis)

# Create a single base mesh data block
mesh = bpy.data.meshes.new("ChainLinkMesh")
bm_base = create_oval_link_mesh(
    major_radius=0.6, 
    minor_radius=0.2, 
    length=3.2, 
    segments_path=48, 
    segments_tube=24
)
bm_base.to_mesh(mesh)
bm_base.free()

# Calculate face count per link to ensure we are well within the 3k - 60k range
# 48 path segments * 24 tube segments = 1152 faces per link.
# 12 links * 1152 = 13,824 total faces. Perfect.

# Instantiate and transform the links
collection = bpy.context.collection

for i in range(num_links):
    obj = bpy.data.objects.new(f"ChainLink_{i:02d}", mesh)
    collection.objects.link(obj)
    
    # Position along Z axis
    z_pos = i * spacing
    
    # Each link is rotated 90 degrees around the chain axis (Z) relative to its neighbour
    # Link 0: rot 0
    # Link 1: rot 90 deg (pi/2)
    # Link 2: rot 180 deg (pi)
    # etc.
    angle = i * (math.pi / 2.0)
    
    # Build transformation matrix
    # Translation along Z, Rotation around Z
    loc_mat = Matrix.Translation(Vector((0.0, 0.0, z_pos)))
    rot_mat = Matrix.Rotation(angle, 4, 'Z')
    
    # To make interlocking correct in alternate planes, 
    # we also apply an initial orientation so alternating links thread through each other.
    # The base link is in XY. 
    # Alternating links need to alternate between XY and YZ planes naturally.
    # A rotation of 90 degrees around Z each step naturally alternates the orientation 
    # of the oval's long axis (X then Y then -X then -Y), creating the classic chain weave.
    
    obj.matrix_world = loc_mat @ rot_mat

# Join all links into a single object to optimize and fulfill "a chain" as a unified asset
bpy.ops.object.select_all(action='DESELECT')
for obj in collection.objects:
    if obj.name.startswith("ChainLink_"):
        obj.select_set(True)

if len(bpy.context.selected_objects) > 0:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    bpy.context.active_object.name = "InterlockingChain"
