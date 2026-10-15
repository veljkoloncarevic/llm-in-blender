import bpy
import bmesh
from mathutils import Vector
import math

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new mesh and object for the vase
mesh = bpy.data.meshes.new("VaseMesh")
vase_obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(vase_obj)
bpy.context.view_layer.objects.active = vase_obj
vase_obj.select_set(True)

# Create bmesh
bm = bmesh.new()

# Define the 2D profile curve for the vase (x, z coordinates)
# The profile will be revolved around the Z axis
# Points: (radius, height)
profile_points = [
    (0.3, 0.0),      # Base center
    (1.0, 0.0),      # Base outer edge
    (1.1, 0.2),      # Lower body
    (1.3, 0.8),      # Wide body
    (1.2, 1.2),      # Upper body
    (0.6, 1.5),      # Neck
    (0.5, 1.8),      # Neck top
    (0.7, 1.85),     # Lip
    (0.6, 1.9),      # Lip inner
]

# Number of segments for the revolution
segments = 64

# Create vertices by revolving the profile around Z axis
vertices = []
for i, (radius, height) in enumerate(profile_points):
    for seg in range(segments):
        angle = (seg / segments) * 2 * math.pi
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = height
        vert = bm.verts.new((x, y, z))
        vertices.append(vert)

# Create faces by connecting the revolved vertices
profile_len = len(profile_points)
for profile_idx in range(profile_len - 1):
    for seg in range(segments):
        # Current segment indices
        next_seg = (seg + 1) % segments
        
        # Vertices for current quad
        v0_idx = profile_idx * segments + seg
        v1_idx = profile_idx * segments + next_seg
        v2_idx = (profile_idx + 1) * segments + next_seg
        v3_idx = (profile_idx + 1) * segments + seg
        
        # Create face
        v0 = vertices[v0_idx]
        v1 = vertices[v1_idx]
        v2 = vertices[v2_idx]
        v3 = vertices[v3_idx]
        
        bm.faces.new([v0, v1, v2, v3])

# Ensure lookup table is updated
bm.normal_update()

# Write bmesh to mesh
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Apply smooth shading
bpy.context.view_layer.objects.active = vase_obj
bpy.ops.object.shade_smooth()

# Add Subdivision Surface modifier
subdiv_modifier = vase_obj.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv_modifier.levels = 3
subdiv_modifier.render_levels = 4

# Recalculate normals and update mesh
mesh.update()

print(f"Vase created with {len(mesh.vertices)} vertices and {len(mesh.polygons)} faces")
