import bpy
import bmesh
from mathutils import Vector, Matrix
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters for (2,3) torus knot
p, q = 2, 3  # Knot parameters
num_points = 400  # Points along the knot curve
tube_radius = 0.15  # Radius of the tube
num_sides = 16  # Sides of the circular cross-section

# Compute the (2,3) torus knot parametric curve
def torus_knot(t, p, q):
    """Compute point on (p,q) torus knot at parameter t in [0, 2*pi]"""
    r = math.cos(q * t) + 2
    x = r * math.cos(p * t)
    y = r * math.sin(p * t)
    z = -math.sin(q * t)
    return Vector([x, y, z])

# Compute tangent vector using finite differences
def tangent(t, p, q, dt=0.001):
    """Compute tangent vector at parameter t"""
    p1 = torus_knot(t - dt, p, q)
    p2 = torus_knot(t + dt, p, q)
    return (p2 - p1).normalized()

# Compute normal vector using Frenet frame
def frenet_frame(t, p, q, dt=0.001):
    """Compute Frenet frame (tangent, normal, binormal) at parameter t"""
    T = tangent(t, p, q, dt)
    
    # Compute second derivative for curvature
    t1 = t - dt
    t2 = t + dt
    p1 = torus_knot(t1, p, q)
    p2 = torus_knot(t, p, q)
    p3 = torus_knot(t2, p, q)
    
    T1 = (p2 - p1).normalized()
    T2 = (p3 - p2).normalized()
    dT = (T2 - T1) / (2 * dt)
    
    # Normal vector
    if dT.length > 0.0001:
        N = dT.normalized()
    else:
        # Fallback: use a vector not parallel to T
        if abs(T.x) < 0.9:
            N = Vector([1, 0, 0])
        else:
            N = Vector([0, 1, 0])
        N = (N - N.dot(T) * T).normalized()
    
    # Binormal
    B = T.cross(N).normalized()
    N = B.cross(T).normalized()
    
    return T, N, B

# Create mesh and object
mesh = bpy.data.meshes.new("TorusKnot")
obj = bpy.data.objects.new("TorusKnot", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Build vertices and faces for the tube
vertices = []
faces = []

# Generate the tube mesh
for i in range(num_points):
    t = (i / num_points) * 2 * math.pi
    center = torus_knot(t, p, q)
    T, N, B = frenet_frame(t, p, q)
    
    # Create circle of vertices around the center
    for j in range(num_sides):
        angle = (j / num_sides) * 2 * math.pi
        offset = tube_radius * (math.cos(angle) * N + math.sin(angle) * B)
        vertex = center + offset
        vertices.append(vertex)

# Create faces connecting the rings
for i in range(num_points):
    next_i = (i + 1) % num_points
    for j in range(num_sides):
        next_j = (j + 1) % num_sides
        
        # Get vertex indices
        v0 = i * num_sides + j
        v1 = i * num_sides + next_j
        v2 = next_i * num_sides + next_j
        v3 = next_i * num_sides + j
        
        # Create quad face
        faces.append([v0, v1, v2, v3])

# Create mesh from vertices and faces
mesh.from_pydata(vertices, [], faces)
mesh.update()

# Smooth shading
for face in mesh.polygons:
    face.use_smooth = True

# Add a simple material for visibility
mat = bpy.data.materials.new(name="TorusKnotMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.5, 0.8, 1.0)
obj.data.materials.append(mat)

print(f"Torus knot (2,3) created with {len(vertices)} vertices and {len(faces)} faces")
