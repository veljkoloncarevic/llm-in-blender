import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a new mesh and object for the vase profile/lathe
mesh = bpy.data.meshes.new("VaseMesh")
obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Define a 2D profile (X, Z coordinates) for a vase:
# Flat base -> wide body -> narrow neck -> flared rim
profile_points = [
    (0.0, 0.0),    # Center bottom (flat base)
    (1.2, 0.0),    # Outer bottom edge
    (1.5, 0.2),    # Lower body outward curve
    (1.8, 0.8),    # Widest body point
    (1.2, 1.8),    # Tapering up to shoulder
    (0.5, 2.2),    # Narrow neck
    (0.5, 2.8),    # Neck straight section
    (0.8, 3.0)     # Flared rim
]

# Number of segments for the revolution around the Z axis
segments = 32

# Rotate the profile points around the Z axis to build the mesh
verts = []
for i in range(segments):
    angle = 2.0 * math.pi * i / segments
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    col_verts = []
    for x, z in profile_points:
        # If x == 0, it's on the axis of rotation, avoid duplicate central vertices per slice
        v = bm.verts.new((x * cos_a, x * sin_a, z))
        col_verts.append(v)
    verts.append(col_verts)

# Build faces connecting the vertices
for i in range(segments):
    next_i = (i + 1) % segments
    current_col = verts[i]
    next_col = verts[next_i]
    
    for j in range(len(profile_points) - 1):
        v1 = current_col[j]
        v2 = next_col[j]
        v3 = next_col[j + 1]
        v4 = current_col[j + 1]
        
        # Skip faces at the exact center bottom if x=0 to avoid degenerate geometry
        if profile_points[j][0] == 0.0 and profile_points[j+1][0] == 0.0:
            continue
            
        bm.faces.new((v1, v2, v3, v4))

# Fill the bottom center if needed, or let subsurf handle/close it.
# Clean up and ensure normals point outward
bm.normal_update()

# Write the bmesh back to the mesh
bm.to_mesh(mesh)
bm.free()

# Set smooth shading for all faces
for poly in mesh.polygons:
    poly.use_smooth = True

# Add a Subdivision Surface modifier to smooth the vase
subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 2

# Select and set active
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
