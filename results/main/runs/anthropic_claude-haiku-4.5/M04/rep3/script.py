import bpy
import bmesh
import math
from mathutils import Vector

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters for (2,3) torus knot
p = 2  # winding number around major circle
q = 3  # winding number around minor circle
major_radius = 3.0
tube_radius = 0.6

# Resolution parameters
knot_segments = 400  # segments along the knot curve
circle_segments = 32  # segments in the circular cross-section

# Function to compute (2,3) torus knot parametric curve
def torus_knot_point(t, p=2, q=3, major_radius=3.0):
    """
    Compute a point on the (p,q) torus knot at parameter t (0 to 2*pi)
    """
    cos_q_t = math.cos(q * t)
    sin_q_t = math.sin(q * t)
    cos_p_t = math.cos(p * t)
    sin_p_t = math.sin(p * t)
    
    # Radius of the curve at this point
    r = major_radius + 2.0 * cos_q_t
    
    # 3D position
    x = r * cos_p_t
    y = r * sin_p_t
    z = -2.0 * sin_q_t
    
    return Vector((x, y, z))

# Function to compute tangent to the knot curve
def torus_knot_tangent(t, p=2, q=3, major_radius=3.0, dt=0.0001):
    """
    Compute tangent vector via numerical differentiation
    """
    p1 = torus_knot_point(t - dt, p, q, major_radius)
    p2 = torus_knot_point(t + dt, p, q, major_radius)
    tangent = (p2 - p1).normalized()
    return tangent

# Build the mesh using bmesh
mesh = bpy.data.meshes.new("TorusKnot")
bm = bmesh.new()

# Generate vertices for the tube
vertices = []
normals = []

for i in range(knot_segments):
    t = (i / knot_segments) * 2 * math.pi
    knot_center = torus_knot_point(t, p, q, major_radius)
    tangent = torus_knot_tangent(t, p, q, major_radius)
    
    # Create perpendicular vectors for the circle cross-section
    # Find a vector not parallel to tangent
    if abs(tangent.x) < 0.9:
        perp1 = Vector((1, 0, 0))
    else:
        perp1 = Vector((0, 1, 0))
    
    perp1 = (perp1 - tangent * tangent.dot(perp1)).normalized()
    perp2 = tangent.cross(perp1).normalized()
    
    # Create circular cross-section
    circle_verts = []
    for j in range(circle_segments):
        angle = (j / circle_segments) * 2 * math.pi
        offset = perp1 * tube_radius * math.cos(angle) + perp2 * tube_radius * math.sin(angle)
        vert_pos = knot_center + offset
        vert = bm.verts.new(vert_pos)
        vertices.append(vert)
        circle_verts.append(vert)
    
    normals.append(circle_verts)

# Create faces connecting consecutive circles
for i in range(knot_segments):
    next_i = (i + 1) % knot_segments
    for j in range(circle_segments):
        next_j = (j + 1) % circle_segments
        
        # Get the four vertices of this quad
        v0 = normals[i][j]
        v1 = normals[i][next_j]
        v2 = normals[next_i][next_j]
        v3 = normals[next_i][j]
        
        # Create face
        bm.faces.new([v0, v1, v2, v3])

# Ensure lookup table is updated
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# Write bmesh to mesh
bm.to_mesh(mesh)
bm.free()

# Create object and link to scene
obj = bpy.data.objects.new("TorusKnot", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Smooth shading
bpy.ops.object.shade_smooth()

# Get face count for verification
face_count = len(mesh.polygons)
print(f"Generated torus knot with {face_count} faces")
