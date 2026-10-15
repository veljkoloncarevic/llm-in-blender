import bpy
import bmesh
from mathutils import Vector
import math

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Parameters for the coil spring
num_turns = 8
radius = 1.0
height = 4.0
wire_radius = 0.15
resolution_helix = 128  # points along the helix per turn
resolution_circle = 32  # points around the wire cross-section

# Create helix curve
helix_points = []
total_points = num_turns * resolution_helix

for i in range(total_points):
    t = i / resolution_helix  # parameter from 0 to num_turns
    angle = t * 2 * math.pi
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = (t / num_turns) * height
    helix_points.append(Vector((x, y, z)))

# Create mesh for the coil spring using a swept approach
mesh = bpy.data.meshes.new("SpringMesh")
bm = bmesh.new()

# Build the spring by creating circular cross-sections along the helix
vertices_list = []

for i, helix_point in enumerate(helix_points):
    # Calculate local coordinate frame for the helix at this point
    t = i / resolution_helix
    angle = t * 2 * math.pi
    
    # Tangent to helix
    dx_dt = -radius * math.sin(angle) * 2 * math.pi / resolution_helix
    dy_dt = radius * math.cos(angle) * 2 * math.pi / resolution_helix
    dz_dt = height / total_points
    
    tangent = Vector((dx_dt, dy_dt, dz_dt)).normalized()
    
    # Create a normal vector perpendicular to tangent
    if abs(tangent.z) < 0.9:
        normal = Vector((0, 0, 1)).cross(tangent).normalized()
    else:
        normal = Vector((1, 0, 0)).cross(tangent).normalized()
    
    binormal = tangent.cross(normal).normalized()
    
    # Create circular cross-section at this helix point
    circle_verts = []
    for j in range(resolution_circle):
        angle_circle = (j / resolution_circle) * 2 * math.pi
        offset = (normal * math.cos(angle_circle) + binormal * math.sin(angle_circle)) * wire_radius
        vert_pos = helix_point + offset
        vert = bm.verts.new(vert_pos)
        circle_verts.append(vert)
    
    vertices_list.append(circle_verts)

# Create faces connecting consecutive circles
for i in range(len(vertices_list) - 1):
    current_circle = vertices_list[i]
    next_circle = vertices_list[i + 1]
    
    for j in range(resolution_circle):
        j_next = (j + 1) % resolution_circle
        
        # Create quad faces
        v0 = current_circle[j]
        v1 = current_circle[j_next]
        v2 = next_circle[j_next]
        v3 = next_circle[j]
        
        try:
            bm.faces.new([v0, v1, v2, v3])
        except:
            pass

# Create closing faces between last and first circles (for continuity)
last_circle = vertices_list[-1]
first_circle = vertices_list[0]

for j in range(resolution_circle):
    j_next = (j + 1) % resolution_circle
    
    v0 = last_circle[j]
    v1 = last_circle[j_next]
    v2 = first_circle[j_next]
    v3 = first_circle[j]
    
    try:
        bm.faces.new([v0, v1, v2, v3])
    except:
        pass

# Finalize mesh
bm.to_mesh(mesh)
bm.free()
mesh.update()

# Create object and link to scene
spring_obj = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(spring_obj)
bpy.context.view_layer.objects.active = spring_obj
spring_obj.select_set(True)

# Apply smooth shading
bpy.ops.object.shade_smooth()

# Get face count for verification
face_count = len(mesh.polygons)
print(f"Coil Spring created with {face_count} faces")
