import bpy
import bmesh
import math
import mathutils

# --- Cleanup Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Parameters ---
num_links = 12
radius_major = 0.6   # Half-length of the oval
radius_minor = 0.3   # Half-width of the oval
tube_radius = 0.08   # Thickness of the link cross-section
segments_major = 32  # Resolution along the oval path
segments_minor = 16  # Resolution of the tube cross-section
# Face count per link = segments_major * segments_minor = 32 * 16 = 512
# Total for 12 links = 6,144 faces (within the 3,000 to 60,000 range)

spacing = 0.7        # Distance between link centers along the X-axis

# --- Base Link Generation via BMesh ---
def create_link_mesh(name):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    # Create an oval (stretching a circle along X)
    # We will build a torus-like geometry along a parametric oval path
    for i in range(segments_major):
        u = i / segments_major
        angle_u = u * 2 * math.pi
        
        # Parametric equations for a flattened oval (stadium-like or scaled circle)
        # Using a superellipse or simple offset for an oval shape:
        # Let's use a standard oval: x = R_maj * cos(u), y = R_min * sin(u)
        x_center = radius_major * math.cos(angle_u)
        y_center = radius_minor * math.sin(angle_u)
        z_center = 0.0
        
        # Derivative to find the tangent for the cross-section orientation
        dx = -radius_major * math.sin(angle_u)
        dy = radius_minor * math.cos(angle_u)
        dz = 0.0
        
        tangent = mathutils.Vector((dx, dy, dz)).normalized()
        # Normal pointing outwards from the center of the oval loop (in XY plane)
        normal = mathutils.Vector((math.cos(angle_u), math.sin(angle_u), 0.0)).normalized()
        # Binormal perpendicular to both
        binormal = tangent.cross(normal).normalized()
        
        # Create ring vertices
        ring_verts = []
        for j in range(segments_minor):
            v = j / segments_minor
            angle_v = v * 2 * math.pi
            
            # Tube offset
            cos_v = math.cos(angle_v)
            sin_v = math.sin(angle_v)
            
            offset = (normal * cos_v + binormal * sin_v) * tube_radius
            vert_pos = mathutils.Vector((x_center, y_center, z_center)) + offset
            
            ring_verts.append(bm.verts.new(vert_pos))
            
    bm.verts.ensure_lookup_table()
    
    # Bridge rings with faces
    for i in range(segments_major):
        next_i = (i + 1) % segments_major
        for j in range(segments_minor):
            next_j = (j + 1) % segments_minor
            
            v0 = bm.verts[i * segments_minor + j]
            v1 = bm.verts[next_i * segments_minor + j]
            v2 = bm.verts[next_i * segments_minor + next_j]
            v3 = bm.verts[i * segments_minor + next_j]
            
            bm.faces.new((v0, v1, v2, v3))
            
    bm.to_mesh(mesh)
    bm.free()
    return mesh

# --- Build the Chain ---
# Create the template mesh
link_mesh = create_link_mdl = create_link_mesh("LinkBase")

objects = []
for i in range(num_links):
    # Create object instance
    obj = bpy.data.objects.new(f"ChainLink_{i:02d}", link_mesh)
    bpy.context.collection.objects.link(obj)
    
    # Position along the X axis
    obj.location.x = i * spacing
    
    # Alternate rotation by 90 degrees around the X-axis (the chain axis)
    # Link 0: 0 deg
    # Link 1: 90 deg
    # Link 2: 0 deg
    # Link 3: 90 deg, etc.
    if i % 2 == 1:
        obj.rotation_euler.x = math.radians(90)
        
    objects.append(obj)

# Optional: Join them into a single chain object for convenience
bpy.ops.object.select_all(action='DESELECT')
for obj in objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = objects[0]
bpy.ops.object.join()

# Rename the final combined chain
bpy.context.active_object.name = "Interlocking_Chain"
