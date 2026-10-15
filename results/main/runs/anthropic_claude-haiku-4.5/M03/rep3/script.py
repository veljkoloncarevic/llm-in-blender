import bpy
import bmesh
from mathutils import Vector
import math

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new mesh and object
mesh = bpy.data.meshes.new("VaseMesh")
vase_obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(vase_obj)
bpy.context.view_layer.objects.active = vase_obj
vase_obj.select_set(True)

# Create bmesh
bm = bmesh.new()

# Define the 2D profile for the vase (X, Z coordinates)
# This profile will be revolved around the Z axis
profile_points = [
    (0.3, 0.0),    # Base center
    (0.35, 0.1),   # Base edge
    (0.4, 0.3),    # Lower body
    (0.5, 0.8),    # Wide body
    (0.48, 1.2),   # Upper body
    (0.3, 1.5),    # Shoulder
    (0.2, 1.8),    # Neck
    (0.15, 2.0),   # Neck top
]

# Number of segments for revolution (determines face count)
num_segments = 128

# Create vertices by revolving the profile
vertices = []
for i, (x, z) in enumerate(profile_points):
    for seg in range(num_segments):
        angle = (seg / num_segments) * 2 * math.pi
        vx = x * math.cos(angle)
        vy = x * math.sin(angle)
        vz = z
        vert = bm.verts.new((vx, vy, vz))
        vertices.append(vert)

# Create faces by connecting adjacent rings
num_profile_points = len(profile_points)
for ring_idx in range(num_profile_points - 1):
    for seg in range(num_segments):
        # Current segment
        v0_idx = ring_idx * num_segments + seg
        v1_idx = ring_idx * num_segments + ((seg + 1) % num_segments)
        
        # Next ring segment
        v2_idx = (ring_idx + 1) * num_segments + ((seg + 1) % num_segments)
        v3_idx = (ring_idx + 1) * num_segments + seg
        
        # Create quad face
        v0 = vertices[v0_idx]
        v1 = vertices[v1_idx]
        v2 = vertices[v2_idx]
        v3 = vertices[v3_idx]
        
        bm.faces.new([v0, v1, v2, v3])

# Ensure lookup table is updated
bm.to_mesh(mesh)
bm.free()

# Smooth shade the object
for face in mesh.polygons:
    face.use_smooth = True

# Add Subdivision Surface modifier
subdiv_mod = vase_obj.modifiers.new(name="Subdivision", type='SUBSURF')
subdiv_mod.levels = 2
subdiv_mod.render_levels = 3

# Update mesh
mesh.update()

# Set smooth shading on the object
bpy.context.view_layer.objects.active = vase_obj
bpy.ops.object.shade_smooth()

print(f"Vase created with {len(mesh.vertices)} vertices and {len(mesh.polygons)} faces")
