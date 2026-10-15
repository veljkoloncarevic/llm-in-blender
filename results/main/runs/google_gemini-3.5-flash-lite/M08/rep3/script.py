import math
import bpy
import bmesh
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_coil_spring():
    # Parameters for the spring
    turns = 8.0
    radius = 1.0
    height = 4.0
    wire_radius = 0.1
    
    # Resolution parameters to hit face count between 2,000 and 60,000
    # Steps per turn (circular cross-section segments)
    # Total vertices along helix = turns * segments_per_turn
    # Total faces roughly = segments_per_turn * radial_segments
    segments_per_turn = 32
    radial_segments = 16
    
    total_steps = int(turns * segments_per_turn)
    
    # Create a new mesh and object
    mesh = bpy.data.meshes.new("CoilSpringMesh")
    obj = bpy.data.objects.new("CoilSpring", mesh)
    
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    
    bm = bmesh.new()
    
    # Generate the helix path points and frames
    path_points = []
    frames = []
    
    for i in range(total_steps + 1):
        t = i / total_steps
        theta = t * turns * 2.0 * math.pi
        
        # Position along the helix
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        z = t * height
        
        pos = Vector((x, y, z))
        path_points.append(pos)
        
        # Tangent vector (derivative of helix position)
        dx = -radius * turns * 2.0 * math.pi * math.sin(theta)
        dy = radius * turns * 2.0 * math.pi * math.cos(theta)
        dz = height
        
        tangent = Vector((dx, dy, dz)).normalized()
        
        # Normal and Bitangent to form a rotation-minimizing-like frame
        # We can use the radial vector pointing towards the center axis as a guide
        radial = Vector((-math.cos(theta), -math.sin(theta), 0.0))
        bitangent = tangent.cross(radial).normalized()
        normal = bitangent.cross(tangent).normalized()
        
        frames.append((normal, bitangent, pos))
        
    # Build the swept tube geometry using bmesh
    # We create rings along the path and connect them
    
    ring_verts_prev = []
    
    for i, (normal, bitangent, pos) in enumerate(frames):
        ring_verts = []
        
        for j in range(radial_segments):
            angle = (j / radial_segments) * 2.0 * math.pi
            # Offset in the normal/bitangent plane
            offset = (normal * math.cos(angle) + bitangent * math.sin(angle)) * wire_radius
            v_pos = pos + offset
            v = bm.verts.new(v_pos)
            ring_verts.append(v)
            
        # Connect current ring to the previous ring with faces
        if i > 0:
            for j in range(radial_segments):
                next_j = (j + 1) % radial_segments
                
                v1 = ring_verts_prev[j]
                v2 = ring_verts_prev[next_j]
                v3 = ring_verts[next_j]
                v4 = ring_verts[j]
                
                bm.faces.new((v1, v2, v3, v4))
                
        ring_verts_prev = ring_verts

    # Cap the ends of the spring tube
    # Start cap
    start_verts = [bm.verts[j] for j in range(radial_segments)]
    # Ensure proper winding for face normal
    bm.faces.new(reversed(start_verts))
    
    # End cap
    end_start_idx = total_steps * radial_segments
    end_verts = [bm.verts[end_start_idx + j] for j in range(radial_segments)]
    bm.faces.new(end_verts)

    # Ensure smooth shading
    bm.normal_update()
    
    # Finish up bmesh to mesh
    bm.to_mesh(mesh)
    bm.free()
    
    # Set smooth shading on the object
    for poly in mesh.polygons:
        poly.use_smooth = True

create_coil_spring()
