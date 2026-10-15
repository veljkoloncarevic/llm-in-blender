import bpy
import bmesh
from mathutils import Matrix, Vector
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_oval_link(radius_major=2.0, radius_minor=0.4, segments=32, ring_segments=16):
    """Create a single oval link using a torus-like approach with oval cross-section."""
    mesh = bpy.data.meshes.new("OvalLink")
    bm = bmesh.new()
    
    verts = []
    
    # Create vertices for an oval link
    # Major radius defines the oval loop, minor radius defines the thickness
    for i in range(segments):
        angle1 = (i / segments) * 2 * math.pi
        
        # Position along the oval loop
        x_oval = radius_major * math.cos(angle1)
        z_oval = radius_major * math.sin(angle1)
        
        for j in range(ring_segments):
            angle2 = (j / ring_segments) * 2 * math.pi
            
            # Create the oval cross-section (ellipse in the plane perpendicular to the loop)
            # The cross-section is in the y-z plane locally
            local_y = radius_minor * 1.5 * math.cos(angle2)  # Make it slightly elongated
            local_z = radius_minor * math.sin(angle2)
            
            # Rotate the cross-section to be perpendicular to the loop tangent
            # Tangent direction at this point
            tangent_x = -math.sin(angle1)
            tangent_z = math.cos(angle1)
            
            # Position in 3D space
            x = x_oval + local_y * tangent_x * 0.5
            y = local_y * 0.866  # Approximate perpendicular component
            z = z_oval + local_y * tangent_z * 0.5 + local_z
            
            verts.append(bm.verts.new((x, y, z)))
    
    # Create faces
    for i in range(segments):
        for j in range(ring_segments):
            v0 = verts[i * ring_segments + j]
            v1 = verts[i * ring_segments + ((j + 1) % ring_segments)]
            v2 = verts[((i + 1) % segments) * ring_segments + ((j + 1) % ring_segments)]
            v3 = verts[((i + 1) % segments) * ring_segments + j]
            
            try:
                bm.faces.new([v0, v1, v2, v3])
            except:
                pass
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    return mesh

def create_chain():
    """Create a chain of 12 interlocking oval links."""
    
    # Create the base oval link mesh once
    link_mesh = create_oval_link(radius_major=2.0, radius_minor=0.4, segments=32, ring_segments=16)
    
    link_objects = []
    
    for i in range(12):
        # Create object from mesh
        link_obj = bpy.data.objects.new(f"Link_{i}", link_mesh)
        bpy.context.collection.objects.link(link_obj)
        
        # Position along the chain axis (Z axis)
        z_offset = i * 1.2
        link_obj.location = (0, 0, z_offset)
        
        # Rotate each link 90 degrees around the Z axis relative to previous
        rotation_angle = (i * math.pi / 2)  # 90 degrees in radians
        link_obj.rotation_euler = (0, 0, rotation_angle)
        
        link_objects.append(link_obj)
    
    return link_objects

# Create the chain
chain = create_chain()

# Set viewport shading to see the geometry clearly
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

print(f"Chain created with {len(chain)} links")
