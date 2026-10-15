import bpy
import bmesh
import math
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
num_teeth = 24
thickness = 0.3
hole_radius = 0.2
module = 1.0  # gear module (pitch diameter / num_teeth)
pitch_radius = (num_teeth * module) / 2.0
addendum = module
dedendum = 1.25 * module
outer_radius = pitch_radius + addendum
root_radius = pitch_radius - dedendum

# Create mesh and object
mesh = bpy.data.meshes.new("SpurGear")
obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(obj)

# Create bmesh
bm = bmesh.new()

# Generate gear tooth profile using involute approximation
def generate_tooth_profile(tooth_index, num_teeth, pitch_radius, outer_radius, root_radius, thickness):
    """Generate vertices for one tooth profile"""
    angle_step = (2 * math.pi) / num_teeth
    base_angle = tooth_index * angle_step
    
    # Tooth half-angle
    tooth_half_angle = angle_step * 0.35
    
    vertices = []
    
    # Root to outer profile (one side of tooth)
    steps = 8
    for i in range(steps + 1):
        t = i / steps
        # Interpolate radius from root to outer
        radius = root_radius + t * (outer_radius - root_radius)
        # Angle follows tooth profile
        angle = base_angle - tooth_half_angle + t * (2 * tooth_half_angle)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        vertices.append((x, y))
    
    # Outer to root profile (other side of tooth)
    for i in range(steps, -1, -1):
        t = i / steps
        radius = root_radius + t * (outer_radius - root_radius)
        angle = base_angle + tooth_half_angle - t * (2 * tooth_half_angle)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        vertices.append((x, y))
    
    return vertices

# Build vertex lists for top and bottom faces
top_verts = []
bottom_verts = []
vert_map = {}  # Map (x, y, z) to vertex index

z_top = thickness / 2.0
z_bottom = -thickness / 2.0

# Generate all teeth vertices
all_tooth_profiles = []
for tooth_idx in range(num_teeth):
    profile = generate_tooth_profile(tooth_idx, num_teeth, pitch_radius, outer_radius, root_radius, thickness)
    all_tooth_profiles.append(profile)
    
    for x, y in profile:
        # Top face vertex
        v_top = bm.verts.new((x, y, z_top))
        top_verts.append(v_top)
        
        # Bottom face vertex
        v_bottom = bm.verts.new((x, y, z_bottom))
        bottom_verts.append(v_bottom)

# Create center hole vertices
hole_steps = 16
hole_top_verts = []
hole_bottom_verts = []

for i in range(hole_steps):
    angle = (2 * math.pi * i) / hole_steps
    x = hole_radius * math.cos(angle)
    y = hole_radius * math.sin(angle)
    
    v_top = bm.verts.new((x, y, z_top))
    hole_top_verts.append(v_top)
    
    v_bottom = bm.verts.new((x, y, z_bottom))
    hole_bottom_verts.append(v_bottom)

# Create faces for teeth (top and bottom)
verts_per_tooth = len(all_tooth_profiles[0])

# Top faces (teeth)
for tooth_idx in range(num_teeth):
    start_idx = tooth_idx * verts_per_tooth
    next_tooth_idx = (tooth_idx + 1) % num_teeth
    next_start_idx = next_tooth_idx * verts_per_tooth
    
    for i in range(verts_per_tooth - 1):
        v1 = top_verts[start_idx + i]
        v2 = top_verts[start_idx + i + 1]
        v3 = top_verts[next_start_idx + i + 1]
        v4 = top_verts[next_start_idx + i]
        
        try:
            bm.faces.new([v1, v2, v3, v4])
        except:
            pass

# Bottom faces (teeth)
for tooth_idx in range(num_teeth):
    start_idx = tooth_idx * verts_per_tooth
    next_tooth_idx = (tooth_idx + 1) % num_teeth
    next_start_idx = next_tooth_idx * verts_per_tooth
    
    for i in range(verts_per_tooth - 1):
        v1 = bottom_verts[start_idx + i]
        v2 = bottom_verts[next_start_idx + i]
        v3 = bottom_verts[next_start_idx + i + 1]
        v4 = bottom_verts[start_idx + i + 1]
        
        try:
            bm.faces.new([v1, v2, v3, v4])
        except:
            pass

# Side faces connecting teeth profiles
for tooth_idx in range(num_teeth):
    start_idx = tooth_idx * verts_per_tooth
    next_start_idx = ((tooth_idx + 1) % num_teeth) * verts_per_tooth
    
    for i in range(verts_per_tooth - 1):
        # Connect top to bottom for each tooth edge
        v1_top = top_verts[start_idx + i]
        v2_top = top_verts[start_idx + i + 1]
        v1_bot = bottom_verts[start_idx + i]
        v2_bot = bottom_verts[start_idx + i + 1]
        
        try:
            bm.faces.new([v1_top, v2_top, v2_bot, v1_bot])
        except:
            pass

# Create hole top and bottom faces
for i in range(hole_steps):
    next_i = (i + 1) % hole_steps
    
    # Top hole face (inward facing)
    try:
        bm.faces.new([hole_top_verts[next_i], hole_top_verts[i]])
    except:
        pass
    
    # Bottom hole face (inward facing)
    try:
        bm.faces.new([hole_bottom_verts[i], hole_bottom_verts[next_i]])
    except:
        pass

# Create hole side faces
for i in range(hole_steps):
    next_i = (i + 1) % hole_steps
    
    v1_top = hole_top_verts[i]
    v2_top = hole_top_verts[next_i]
    v1_bot = hole_bottom_verts[i]
    v2_bot = hole_bottom_verts[next_i]
    
    try:
        bm.faces.new([v1_top, v1_bot, v2_bot, v2_top])
    except:
        pass

# Finalize mesh
bm.to_mesh(mesh)
bm.free()

# Update mesh
mesh.update()

# Add smooth shading
for face in mesh.polygons:
    face.use_smooth = True

# Create material for visibility
mat = bpy.data.materials.new(name="GearMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)
obj.data.materials.append(mat)

# Set object as active
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
