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
pitch_radius = 5.0  # Base radius for the gear
addendum = 0.5  # Height of tooth above pitch circle
dedendum = 0.3  # Depth of tooth below pitch circle
hole_radius = 1.0  # Center hole radius
tooth_width_ratio = 0.4  # Width of tooth relative to pitch

# Calculate radii
outer_radius = pitch_radius + addendum
root_radius = pitch_radius - dedendum
inner_radius = hole_radius

# Create mesh and object
mesh = bpy.data.meshes.new("SpurGear")
gear_obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(gear_obj)
bpy.context.view_layer.objects.active = gear_obj
gear_obj.select_set(True)

# Create bmesh
bm = bmesh.new()

# Generate vertices
verts = []
tooth_angle = (2 * math.pi) / num_teeth
half_tooth_angle = tooth_angle * tooth_width_ratio / 2

# Top face vertices (z = thickness/2)
z_top = thickness / 2

# Bottom face vertices (z = -thickness/2)
z_bottom = -thickness / 2

# Create vertices for top and bottom faces
# We'll create: hole circle, root circle, tooth profile
vertices_per_tooth = 4  # Per tooth on pitch circle area
total_tooth_verts = num_teeth * vertices_per_tooth

# Hole vertices (inner circle)
hole_verts_top = []
hole_verts_bottom = []
for i in range(num_teeth * 2):  # Double resolution for hole
    angle = (i / (num_teeth * 2)) * 2 * math.pi
    x = inner_radius * math.cos(angle)
    y = inner_radius * math.sin(angle)
    hole_verts_top.append(bm.verts.new((x, y, z_top)))
    hole_verts_bottom.append(bm.verts.new((x, y, z_bottom)))

# Root and tooth vertices
root_verts_top = []
root_verts_bottom = []
outer_verts_top = []
outer_verts_bottom = []

for tooth_idx in range(num_teeth):
    base_angle = tooth_idx * tooth_angle
    
    # Root circle points (base of tooth)
    angle1 = base_angle - half_tooth_angle - tooth_angle * 0.2
    angle2 = base_angle + half_tooth_angle + tooth_angle * 0.2
    
    # Root points
    x1 = root_radius * math.cos(angle1)
    y1 = root_radius * math.sin(angle1)
    x2 = root_radius * math.cos(angle2)
    y2 = root_radius * math.sin(angle2)
    
    root_verts_top.append(bm.verts.new((x1, y1, z_top)))
    root_verts_bottom.append(bm.verts.new((x1, y1, z_bottom)))
    root_verts_top.append(bm.verts.new((x2, y2, z_top)))
    root_verts_bottom.append(bm.verts.new((x2, y2, z_bottom)))
    
    # Outer tooth points
    angle3 = base_angle - half_tooth_angle
    angle4 = base_angle + half_tooth_angle
    
    x3 = outer_radius * math.cos(angle3)
    y3 = outer_radius * math.sin(angle3)
    x4 = outer_radius * math.cos(angle4)
    y4 = outer_radius * math.sin(angle4)
    
    outer_verts_top.append(bm.verts.new((x3, y3, z_top)))
    outer_verts_bottom.append(bm.verts.new((x3, y3, z_bottom)))
    outer_verts_top.append(bm.verts.new((x4, y4, z_top)))
    outer_verts_bottom.append(bm.verts.new((x4, y4, z_bottom)))

# Create faces
# Top face
for i in range(len(hole_verts_top) - 1):
    try:
        bm.faces.new([hole_verts_top[i], hole_verts_top[i + 1], root_verts_top[i % len(root_verts_top)]])
    except:
        pass

# Create tooth faces on top
for tooth_idx in range(num_teeth):
    r_idx = tooth_idx * 2
    o_idx = tooth_idx * 2
    
    # Connect root to outer tooth points
    try:
        bm.faces.new([root_verts_top[r_idx], outer_verts_top[o_idx], outer_verts_top[o_idx + 1], root_verts_top[r_idx + 1]])
    except:
        pass

# Bottom face (same connectivity but reversed)
for i in range(len(hole_verts_bottom) - 1):
    try:
        bm.faces.new([hole_verts_bottom[i + 1], hole_verts_bottom[i], root_verts_bottom[i % len(root_verts_bottom)]])
    except:
        pass

for tooth_idx in range(num_teeth):
    r_idx = tooth_idx * 2
    o_idx = tooth_idx * 2
    
    try:
        bm.faces.new([root_verts_bottom[r_idx], root_verts_bottom[r_idx + 1], outer_verts_bottom[o_idx + 1], outer_verts_bottom[o_idx]])
    except:
        pass

# Side faces connecting top and bottom
# Hole sides
for i in range(len(hole_verts_top) - 1):
    try:
        bm.faces.new([hole_verts_top[i], hole_verts_top[i + 1], hole_verts_bottom[i + 1], hole_verts_bottom[i]])
    except:
        pass

# Root sides
for i in range(len(root_verts_top) - 1):
    try:
        bm.faces.new([root_verts_top[i], root_verts_top[i + 1], root_verts_bottom[i + 1], root_verts_bottom[i]])
    except:
        pass

# Outer tooth sides
for i in range(len(outer_verts_top) - 1):
    try:
        bm.faces.new([outer_verts_top[i], outer_verts_top[i + 1], outer_verts_bottom[i + 1], outer_verts_bottom[i]])
    except:
        pass

# Finalize mesh
bm.to_mesh(mesh)
bm.free()
mesh.update()

# Apply smooth shading
bpy.context.view_layer.objects.active = gear_obj
bpy.ops.object.shade_smooth()
