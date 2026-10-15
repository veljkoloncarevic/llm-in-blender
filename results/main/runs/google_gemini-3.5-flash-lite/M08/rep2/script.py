import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the coil spring
turns = 8
radius = 1.0
height = 4.0
wire_radius = 0.1
resolution_turns = 32  # Segments per full 360-degree turn
resolution_wire = 12   # Vertices around the circular cross-section of the wire

total_segments = turns * resolution_turns
total_height = height

# Create a BMesh for the spring
bm = bmesh.new()

# Generate the helix vertices and build rings (circular cross-sections) along the path
rings = []

for i in range(total_segments + 1):
    t = i / total_segments
    angle = t * turns * 2.0 * math.pi
    
    # Helix position
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = t * total_height
    
    center = mathutils_Vector = (x, y, z)
    
    # Calculate tangent of the helix to orient the cross-section
    # Derivative of helix: (-r*w*sin(wt), r*w*cos(wt), h)
    w = turns * 2.0 * math.pi
    dx = -radius * w * math.sin(angle)
    dy = radius * w * math.cos(angle)
    dz = total_height
    
    tangent = bpy.types.Mesh.__annotations__ # dummy, use mathutils
    from mathutils import Vector
    tan = Vector((dx, dy, dz)).normalized()
    
    # Find normal and binormal for cross-section
    # Arbitrary vector not parallel to tangent
    if abs(tan.z) < 0.99:
        normal = Vector((0, 0, 1)).cross(tan).normalized()
    else:
        normal = Vector((1, 0, 0)).cross(tan).normalized()
    binormal = tan.cross(normal).normalized()
    
    # Create ring vertices
    ring_verts = []
    for j in range(resolution_wire):
        theta = (j / resolution_wire) * 2.0 * math.pi
        offset = (normal * math.cos(theta) + binormal * math.sin(theta)) * wire_radius
        v_pos = Vector((x, y, z)) + offset
        ring_verts.append(bm.verts.new(v_pos))
        
    rings.append(ring_verts)

# Connect rings with faces
for i in range(total_segments):
    r1 = rings[i]
    r2 = rings[i + 1]
    n = resolution_wire
    for j in range(n):
        next_j = (j + 1) % n
        v1 = r1[j]
        v2 = r1[next_j]
        v3 = r2[next_j]
        v4 = r2[j]
        bm.faces.new((v1, v2, v3, v4))

# Cap the ends
cap1_verts = [v for v in rings[0]]
cap1_verts.reverse() # ensure correct normal
bm.faces.new(cap1_verts)

cap2_verts = [v for v in rings[-1]]
bm.faces.new(cap2_verts)

# Create mesh and object
mesh = bpy.data.meshes.new("CoilSpringMesh")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("CoilSpring", mesh)
bpy.context.collection.objects.link(obj)

# Set smooth shading
for f in mesh.polygons:
    f.use_smooth = True

# Select the object
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
