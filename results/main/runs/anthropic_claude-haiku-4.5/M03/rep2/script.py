import bpy
import bmesh
from mathutils import Vector
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a 2D profile for the vase (side view)
# Points: (radius, height) - will be revolved around Z axis
profile_points = [
    (0.3, 0.0),      # base center
    (0.8, 0.0),      # base outer
    (0.9, 0.3),      # lower body
    (1.2, 1.5),      # wide body
    (1.1, 2.5),      # upper body
    (0.5, 3.0),      # narrow neck
    (0.55, 3.3),     # neck rim
]

# Number of segments for revolution (affects face count)
num_segments = 64

# Create mesh and object
mesh = bpy.data.meshes.new("VaseMesh")
obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Use bmesh to build the lathe geometry
bm = bmesh.new()

# Create vertices by revolving the profile around the Z axis
vertices = []
for segment in range(num_segments):
    angle = (segment / num_segments) * 2 * math.pi
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    segment_verts = []
    for radius, height in profile_points:
        x = radius * cos_a
        y = radius * sin_a
        z = height
        vert = bm.verts.new((x, y, z))
        segment_verts.append(vert)
    vertices.append(segment_verts)

# Create faces by connecting adjacent segments
num_profile_points = len(profile_points)
for segment in range(num_segments):
    next_segment = (segment + 1) % num_segments
    
    for profile_idx in range(num_profile_points - 1):
        # Get the four corners of the quad
        v0 = vertices[segment][profile_idx]
        v1 = vertices[segment][profile_idx + 1]
        v2 = vertices[next_segment][profile_idx + 1]
        v3 = vertices[next_segment][profile_idx]
        
        # Create face (quad)
        bm.faces.new([v0, v1, v2, v3])

# Ensure lookup table is up to date
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Apply smooth shading
bpy.context.view_layer.objects.active = obj
bpy.ops.object.shade_smooth()

# Add Subdivision Surface modifier
subdiv = obj.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv.levels = 2
subdiv.render_levels = 3

# Recalculate normals
mesh.update()

# Apply smooth shading to the object
bpy.ops.object.shade_smooth()

# Center the object
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')

# Print face count for verification
face_count = len(mesh.polygons)
print(f"Vase created with {face_count} faces")
