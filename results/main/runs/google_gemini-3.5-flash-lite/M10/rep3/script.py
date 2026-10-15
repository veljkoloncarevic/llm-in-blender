import bpy
import bmesh
import math
from mathutils import Matrix, Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_oval_link_mesh(major_radius=1.0, minor_radius=0.35, length=2.0, segments_path=32, segments_ring=16):
    """
    Creates a procedural oval link (stadium shape revolved/swept with a circle).
    """
    bm = bmesh.new()
    
    # We construct an oval path (two semicircles connected by straight segments along X-axis)
    # Total length of straight part is 'length'. Radius of semicircles is 'major_radius'.
    # Actually, let's define an oval using parametric points:
    # Half-length of the straight section
    hl = length * 0.5
    
    # Generate profile circle (in YZ plane)
    profile_verts = []
    for i in range(segments_ring):
        angle = 2.0 * math.pi * i / segments_ring
        y = minor_radius * math.cos(angle)
        z = minor_radius * math.sin(angle)
        profile_verts.append((0.0, y, z))
        
    # Generate path points for the oval
    # We want smooth transitions. Let's make a path with semicircular ends.
    path_verts = []
    half_path_segs = segments_path // 2
    
    # Right semicircle
    for i in range(half_path_segs + 1):
        angle = math.pi * 0.5 - math.pi * i / half_path_segs
        x = hl + major_radius * math.sin(angle)
        z_offset = major_radius * math.cos(angle) # wait, let's keep path in XY or XZ. 
        # Let's keep the link flat on XY plane and extrude along Z? 
        浦 # Better: Path in XY plane.
        # Right end cap (centered at x = hl, y = 0)
    
    # Let's use a simpler, robust approach: bmesh primitive add torus or custom loft,
    # or just build vertices manually for an exact stadium-profile sweep.
    
    total_path_steps = segments_path
    path = []
    for i in range(total_path_steps):
        t = i / total_path_steps
        theta = t * 2.0 * math.pi
        
        # Superformula or simple stadium parametric:
        # Let's do a stadium: 
        # If angle is between -pi/2 and pi/2: x = hl + r*cos, y = r*sin
        # Else: x = -hl + r*cos, y = r*sin ... wait, standard parametric for oval:
        # Let's use a mathematically clean formulation:
        # A rectangle from -hl to hl of width 2*r, capped by half circles.
        
        # Easier: just use bmesh to create a subdivided cube/cylinder and bend it, 
        # or construct ring by ring.
        pass

    # Alternative precise construction: Ring-by-ring generation
    # Path goes around the center (0,0,0) with overall dimensions: length + 2*major_radius by 2*major_radius
    
    verts_ring_list = []
    
    # Number of steps along the oval path
    n_path = segments_path
    n_ring = segments_ring
    
    # We define the center line of the oval in the XY plane
    # Straight parts along X: from -L/2 to +L/2 at y = +R and y = -R
    # Ends: semicircles of radius R
    
    R = major_radius
    L = length
    perimeter = 2.0 * L + 2.0 * math.pi * R
    
    path_points = []
    path_tangents = []
    
    for i in range(n_path):
        s = (i / n_path) * perimeter
        # Determine position based on distance s along perimeter
        if s < L:
            # Top straight section (moving right)
            x = -L/2 + s
            y = R
            dx, dy = 1.0, 0.0
        elif s < L + math.pi * R:
            # Right semicircle
            s2 = s - L
            phi = math.pi/2 - s2 / R
            x = L/2 + R * math.cos(phi)
            y = R * math.sin(phi)
            dx, dy = -math.sin(phi), math.cos(phi)
        elif s < 2.0 * L + math.pi * R:
            # Bottom straight section (moving left)
            s2 = s - (L + math.pi * R)
            x = L/2 - s2
            y = -R
            dx, dy = -1.0, 0.0
        else:
            # Left semicircle
            s2 = s - (2.0 * L + math.pi * R)
            phi = -math.pi/2 - s2 / R
            x = -L/2 + R * math.cos(phi)
            y = R * math.sin(phi)
            dx, dy = -math.sin(phi), math.cos(phi)
            
        path_points.append(Vector((x, y, 0.0)))
        # Tangent vector
        tan = Vector((dx, dy, 0.0)).normalized()
        path_tangents.append(tan)

    # Now sweep the minor circle along the path
    ring_verts_matrix = []
    
    for i in range(n_path):
        p = path_points[i]
        tan = path_tangents[i]
        
        # Normal in XY plane is (-tan.y, tan.x, 0)
        normal = Vector((-tan.y, tan.x, 0.0))
        # Binormal is Z axis (0, 0, 1)
        binormal = Vector((0.0, 0.0, 1.0))
        
        ring = []
        for j in range(n_ring):
            angle = 2.0 * math.pi * j / n_ring
            # local offset in normal/binormal plane
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            
            offset = normal * (cos_a * minor_radius) + binormal * (sin_a * minor_radius)
            ring.append(bm.verts.new(p + offset))
        ring_verts_matrix.append(ring)
        
    # Connect rings with faces
    for i in range(n_path):
        next_i = (i + 1) % n_path
        ring_a = ring_verts_matrix[i]
        ring_b = ring_verts_matrix[next_i]
        
        for j in range(n_ring):
            next_j = (j + 1) % n_ring
            v1 = ring_a[j]
            v2 = ring_a[next_j]
            v3 = ring_b[next_j]
            v4 = ring_b[j]
            
            bm.faces.new((v1, v2, v3, v4))
            
    bm.normal_update()
    return bm

# Parameters for the chain
num_links = 12
major_r = 0.8
minor_r = 0.25
link_len = 1.2
seg_path = 48
seg_ring = 24

# Each link has about seg_path * seg_ring faces. 
# 48 * 24 = 1152 faces per link. 12 links * 1152 = 13,824 faces (fits well in 3k-60k range).

# Create base mesh data
bm_base = create_oval_link_mesh(major_radius=major_r, minor_radius=minor_r, length=link_len, 
                                segments_path=seg_path, segments_ring=seg_ring)

mesh_data = bpy.data.meshes.new("ChainLinkMesh")
bm_base.to_mesh(mesh_data)
bm_base.free()

# Create collection of linked objects
# Spacing between interlocking links: 
# The links pass through each other's ends. 
# Effective center-to-center distance along the chain axis (X) should be slightly less than (link_len + 2*major_r)
spacing = link_len + major_r * 0.8

link_objects = []

for i in range(num_links):
    obj = bpy.data.objects.new(f"ChainLink_{i:02d}", mesh_data)
    bpy.context.collection.objects.link(obj)
    
    # Position along X axis
    x_pos = i * spacing - (num_links - 1) * spacing * 0.5
    obj.location = Vector((x_pos, 0.0, 0.0))
    
    # Rotate 90 degrees around the chain axis (X axis) relative to neighbour
    # i.e., alternating 0 and 90 degrees roll
    roll_angle = math.radians(90.0 * i)
    obj.rotation_euler = Vector((roll_angle, 0.0, 0.0))
    
    link_objects.append(obj)

# Optional: Join them into a single object for a clean scene structure and unified face count
bpy.ops.object.select_all(action='DESELECT')
for obj in link_objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = link_objects[0]
bpy.ops.object.join()

final_obj = bpy.context.view_layer.objects.active
final_obj.name = "InterlockingChain"

# Shade smooth for clean appearance
for p in final_obj.data.polygons:
    p.use_smooth = True
