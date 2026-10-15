import bpy
import bmesh
from mathutils import Matrix, Vector, Euler
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_oval_link(radius_major=2.0, radius_minor=0.5, segments=32, rings=16):
    """Create a single oval link using a torus-like approach"""
    mesh = bpy.data.meshes.new("OvalLinkMesh")
    obj = bpy.data.objects.new("OvalLink", mesh)
    
    bm = bmesh.new()
    
    # Create vertices for an oval torus
    # Major radius creates the oval shape
    # Minor radius creates the thickness of the link
    verts = []
    
    for i in range(segments):
        theta = (i / segments) * 2 * math.pi
        # Oval shape in XY plane
        x_oval = radius_major * math.cos(theta)
        y_oval = radius_major * 0.6 * math.sin(theta)  # 0.6 factor makes it oval-shaped
        
        for j in range(rings):
            phi = (j / rings) * 2 * math.pi
            # Add thickness around the oval path
            x = x_oval + radius_minor * math.cos(phi) * math.cos(theta)
            y = y_oval + radius_minor * math.cos(phi) * math.sin(theta)
            z = radius_minor * math.sin(phi)
            
            v = bm.verts.new((x, y, z))
            verts.append(v)
    
    # Create faces
    for i in range(segments):
        for j in range(rings):
            v0 = verts[i * rings + j]
            v1 = verts[i * rings + (j + 1) % rings]
            v2 = verts[((i + 1) % segments) * rings + (j + 1) % rings]
            v3 = verts[((i + 1) % segments) * rings + j]
            
            bm.faces.new([v0, v1, v2, v3])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return obj

# Create 12 interlocking links
num_links = 12
spacing = 1.5

for i in range(num_links):
    # Create a new link
    link = create_oval_link(radius_major=2.0, radius_minor=0.5, segments=32, rings=16)
    
    # Position along Z axis
    link.location.z = i * spacing
    
    # Rotate 90 degrees around Z axis relative to previous link
    rotation_angle = (i * 90) * (math.pi / 180)
    
    # Apply rotation around Z axis
    link.rotation_euler = Euler((0, 0, rotation_angle), 'XYZ')
    
    # Link the object to the scene
    bpy.context.collection.objects.link(link)
    bpy.context.view_layer.objects.active = link
    link.select_set(True)

print("Chain of 12 interlocking oval links created successfully")
