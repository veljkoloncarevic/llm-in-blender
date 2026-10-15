import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters for (2,3) torus knot
p, q = 2, 3
num_segments = 400  # segments along the knot curve
tube_radius = 0.15
tube_segments = 24  # segments around the tube cross-section

# Generate the (2,3) torus knot curve
def torus_knot(t, p, q):
    """Parametric equation for a (p,q) torus knot"""
    r = math.cos(q * t) + 2
    x = r * math.cos(p * t)
    y = r * math.sin(p * t)
    z = -math.sin(q * t)
    return Vector((x, y, z))

# Generate curve points
curve_points = []
for i in range(num_segments):
    t = 2 * math.pi * i / num_segments
    curve_points.append(torus_knot(t, p, q))

# Function to get perpendicular vectors for tube cross-section
def get_perpendicular_vectors(tangent):
    """Get two perpendicular vectors to the tangent"""
    tangent = tangent.normalized()
    
    # Find a vector not parallel to tangent
    if abs(tangent.x) < 0.9:
        up = Vector((1, 0, 0))
    else:
        up = Vector((0, 1, 0))
    
    # Create perpendicular vectors using cross product
    right = tangent.cross(up).normalized()
    actual_up = right.cross(tangent).normalized()
    
    return right, actual_up

# Create mesh and bmesh
mesh = bpy.data.meshes.new("TorusKnot")
obj = bpy.data.objects.new("TorusKnot", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

bm = bmesh.new()

# Generate tube vertices by sweeping a circle along the knot curve
vertices_grid = []

for i in range(num_segments):
    current_point = curve_points[i]
    next_point = curve_points[(i + 1) % num_segments]
    
    # Compute tangent vector
    tangent = next_point - current_point
    
    # Get perpendicular vectors
    right, up = get_perpendicular_vectors(tangent)
    
    # Create circle of vertices around this point
    circle_verts = []
    for j in range(tube_segments):
        angle = 2 * math.pi * j / tube_segments
        offset = right * (tube_radius * math.cos(angle)) + up * (tube_radius * math.sin(angle))
        vert_pos = current_point + offset
        vert = bm.verts.new(vert_pos)
        circle_verts.append(vert)
    
    vertices_grid.append(circle_verts)

# Create faces connecting the tube segments
for i in range(num_segments):
    for j in range(tube_segments):
        # Get indices for current and next ring
        current_ring = vertices_grid[i]
        next_ring = vertices_grid[(i + 1) % num_segments]
        
        v1 = current_ring[j]
        v2 = current_ring[(j + 1) % tube_segments]
        v3 = next_ring[(j + 1) % tube_segments]
        v4 = next_ring[j]
        
        # Create quad face
        bm.faces.new([v1, v2, v3, v4])

# Ensure lookup table and write to mesh
bm.to_mesh(mesh)
mesh.update()
bm.free()

# Smooth shading
bpy.context.view_layer.objects.active = obj
bpy.ops.object.shade_smooth()

# Add a simple material for visibility
mat = bpy.data.materials.new(name="TorusKnotMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.1, 0.5, 0.9, 1.0)  # Blue color
obj.data.materials.append(mat)

print(f"Torus knot created with {len(mesh.vertices)} vertices and {len(mesh.polygons)} faces")
