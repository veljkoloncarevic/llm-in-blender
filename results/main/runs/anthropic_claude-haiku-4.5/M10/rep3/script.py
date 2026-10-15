import bpy
import bmesh
from mathutils import Matrix, Vector, Quaternion
import math

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_oval_link(radius_major=2.0, radius_minor=0.5, segments=32, rings=16):
    """Create a single oval link using a torus-like approach with oval cross-section"""
    mesh = bpy.data.meshes.new("OvalLink")
    bm = bmesh.new()
    
    vertices = []
    
    # Create vertices for a torus with oval cross-section
    for i in range(segments):
        theta = (i / segments) * 2 * math.pi
        for j in range(rings):
            phi = (j / rings) * 2 * math.pi
            
            # Major radius circle
            x = (radius_major + radius_minor * math.cos(phi)) * math.cos(theta)
            y = (radius_major + radius_minor * math.cos(phi)) * math.sin(theta)
            # Oval in z direction - use 1.5x height for oval shape
            z = radius_minor * 1.5 * math.sin(phi)
            
            v = bm.verts.new((x, y, z))
            vertices.append(v)
    
    # Create faces
    for i in range(segments):
        for j in range(rings):
            v0 = vertices[i * rings + j]
            v1 = vertices[i * rings + ((j + 1) % rings)]
            v2 = vertices[((i + 1) % segments) * rings + ((j + 1) % rings)]
            v3 = vertices[((i + 1) % segments) * rings + j]
            
            bm.faces.new([v0, v1, v2, v3])
    
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    
    obj = bpy.data.objects.new("OvalLink", mesh)
    bpy.context.collection.objects.link(obj)
    
    return obj

def create_chain(num_links=12, link_spacing=1.2, major_radius=2.0):
    """Create a chain of interlocking oval links"""
    links = []
    
    for i in range(num_links):
        # Create the link
        link = create_oval_link(radius_major=major_radius, radius_minor=0.5, segments=32, rings=16)
        
        # Position along z-axis
        link.location.z = i * link_spacing
        
        # Rotate 90 degrees around z-axis for each successive link
        rotation_angle = (i * math.pi / 2)
        quat = Quaternion((0, 0, 1), rotation_angle)
        link.rotation_quaternion = quat
        
        links.append(link)
    
    return links

# Create the chain
chain_links = create_chain(num_links=12, link_spacing=1.2, major_radius=2.0)

# Join all links into a single object for efficiency
bpy.context.view_layer.objects.active = chain_links[0]
for link in chain_links[1:]:
    link.select_set(True)
chain_links[0].select_set(True)

bpy.ops.object.join()

# Get the final object
final_obj = bpy.context.view_layer.objects.active
final_obj.name = "ChainOfLinks"

print(f"Created chain with {len(chain_links)} interlocking oval links")
print(f"Total vertices: {len(final_obj.data.vertices)}")
print(f"Total faces: {len(final_obj.data.polygons)}")
