import bpy
import bmesh
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gear parameters
num_teeth = 24
thickness = 0.3
module = 1.0  # Pitch circle diameter / number of teeth
pitch_radius = (num_teeth * module) / 2.0
addendum = module
dedendum = 1.25 * module
outer_radius = pitch_radius + addendum
root_radius = pitch_radius - dedendum
hole_radius = 0.5

# Create mesh and object
mesh = bpy.data.meshes.new("SpurGear")
obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(obj)

# Create bmesh
bm = bmesh.new()

# Generate gear tooth profile
def create_tooth_profile(angle_offset, pitch_rad, outer_rad, root_rad, tooth_width=0.3):
    """Create a single tooth profile"""
    tooth_angle = (2 * math.pi) / num_teeth
    half_tooth = tooth_width / pitch_rad / 2
    
    # Tooth flank angles
    pressure_angle = math.radians(20)
    
    points = []
    
    # Root circle points
    angle1 = angle_offset - half_tooth * 1.5
    angle2 = angle_offset + half_tooth * 1.5
    points.append(Vector((root_rad * math.cos(angle1), root_rad * math.sin(angle1), 0)))
    points.append(Vector((root_rad * math.cos(angle2), root_rad * math.sin(angle2), 0)))
    
    # Outer circle points (tooth tip)
    angle3 = angle_offset - half_tooth * 0.8
    angle4 = angle_offset + half_tooth * 0.8
    points.append(Vector((outer_rad * math.cos(angle3), outer_rad * math.sin(angle3), 0)))
    points.append(Vector((outer_rad * math.cos(angle4), outer_rad * math.sin(angle4), 0)))
    
    return points

# Create vertices for top and bottom faces
vertices_top = []
vertices_bottom = []

# Generate teeth
for tooth_idx in range(num_teeth):
    angle_offset = (2 * math.pi * tooth_idx) / num_teeth
    
    # Create intermediate radius points for smoother teeth
    num_points_per_tooth = 8
    
    for pt_idx in range(num_points_per_tooth):
        t = pt_idx / (num_points_per_tooth - 1)
        
        # Vary radius along tooth
        if t < 0.25:
            # Root to outer flank
            r = root_radius + (outer_radius - root_radius) * (t / 0.25)
            angle = angle_offset - (math.pi / num_teeth) * (1 - 4*t)
        elif t < 0.75:
            # Outer region
            r = outer_radius
            angle = angle_offset - (math.pi / num_teeth) * (1 - 2*(t-0.25))
        else:
            # Outer to root other flank
            r = outer_radius - (outer_radius - root_radius) * ((t - 0.75) / 0.25)
            angle = angle_offset + (math.pi / num_teeth) * (4*(t-0.75) - 1)
        
        # Top vertices
        v_top = Vector((r * math.cos(angle), r * math.sin(angle), thickness / 2))
        vertices_top.append(bm.verts.new(v_top))
        
        # Bottom vertices
        v_bottom = Vector((r * math.cos(angle), r * math.sin(angle), -thickness / 2))
        vertices_bottom.append(bm.verts.new(v_bottom))

# Add hole vertices
hole_verts_top = []
hole_verts_bottom = []
num_hole_segments = 16

for i in range(num_hole_segments):
    angle = (2 * math.pi * i) / num_hole_segments
    v_top = Vector((hole_radius * math.cos(angle), hole_radius * math.sin(angle), thickness / 2))
    hole_verts_top.append(bm.verts.new(v_top))
    
    v_bottom = Vector((hole_radius * math.cos(angle), hole_radius * math.sin(angle), -thickness / 2))
    hole_verts_bottom.append(bm.verts.new(v_bottom))

# Create faces for teeth (top)
points_per_tooth = 8
for tooth_idx in range(num_teeth):
    start_idx = tooth_idx * points_per_tooth
    next_start = ((tooth_idx + 1) % num_teeth) * points_per_tooth
    
    for pt_idx in range(points_per_tooth - 1):
        v0 = vertices_top[start_idx + pt_idx]
        v1 = vertices_top[start_idx + pt_idx + 1]
        v2 = vertices_top[next_start + pt_idx + 1]
        v3 = vertices_top[next_start + pt_idx]
        
        try:
            bm.faces.new([v0, v1, v2, v3])
        except:
            pass

# Create faces for teeth (bottom)
for tooth_idx in range(num_teeth):
    start_idx = tooth_idx * points_per_tooth
    next_start = ((tooth_idx + 1) % num_teeth) * points_per_tooth
    
    for pt_idx in range(points_per_tooth - 1):
        v0 = vertices_bottom[start_idx + pt_idx]
        v1 = vertices_bottom[start_idx + pt_idx + 1]
        v2 = vertices_bottom[next_start + pt_idx + 1]
        v3 = vertices_bottom[next_start + pt_idx]
        
        try:
            bm.faces.new([v3, v2, v1, v0])
        except:
            pass

# Create side faces connecting top and bottom
total_verts = num_teeth * points_per_tooth
for i in range(total_verts):
    next_i = (i + 1) % total_verts
    v0 = vertices_top[i]
    v1 = vertices_top[next_i]
    v2 = vertices_bottom[next_i]
    v3 = vertices_bottom[i]
    
    try:
        bm.faces.new([v0, v1, v2, v3])
    except:
        pass

# Create hole faces (top)
for i in range(num_hole_segments):
    next_i = (i + 1) % num_hole_segments
    v0 = hole_verts_top[i]
    v1 = hole_verts_top[next_i]
    v2 = hole_verts_bottom[next_i]
    v3 = hole_verts_bottom[i]
    
    try:
        bm.faces.new([v0, v3, v2, v1])
    except:
        pass

# Finalize bmesh
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Set smooth shading
bpy.context.view_layer.objects.active = obj
bpy.ops.object.shade_smooth()
