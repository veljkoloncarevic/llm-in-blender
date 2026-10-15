import bpy
import bmesh
from mathutils import Vector, Matrix
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
num_steps = 24
step_rotation = 15  # degrees per step
step_height = 0.3  # vertical distance per step
column_radius = 0.5
step_radius = 2.0  # distance from center to step
step_width = 0.8  # width of each step
step_depth = 0.5  # depth of each step
handrail_radius = step_radius + 0.3  # slightly outside steps
handrail_thickness = 0.08

# Create main mesh object
mesh = bpy.data.meshes.new("SpiralStaircase")
obj = bpy.data.objects.new("SpiralStaircase", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

bm = bmesh.new()

# Build central cylinder column
cylinder_height = num_steps * step_height
cylinder_verts_bottom = []
cylinder_verts_top = []
num_cylinder_sides = 16

for i in range(num_cylinder_sides):
    angle = (i / num_cylinder_sides) * 2 * math.pi
    x = column_radius * math.cos(angle)
    y = column_radius * math.sin(angle)
    cylinder_verts_bottom.append(bm.verts.new((x, y, 0)))
    cylinder_verts_top.append(bm.verts.new((x, y, cylinder_height)))

# Create cylinder side faces
for i in range(num_cylinder_sides):
    next_i = (i + 1) % num_cylinder_sides
    bm.faces.new([
        cylinder_verts_bottom[i],
        cylinder_verts_bottom[next_i],
        cylinder_verts_top[next_i],
        cylinder_verts_top[i]
    ])

# Create cylinder top and bottom caps
bottom_center = bm.verts.new((0, 0, 0))
top_center = bm.verts.new((0, 0, cylinder_height))

for i in range(num_cylinder_sides):
    next_i = (i + 1) % num_cylinder_sides
    bm.faces.new([bottom_center, cylinder_verts_bottom[next_i], cylinder_verts_bottom[i]])
    bm.faces.new([top_center, cylinder_verts_top[i], cylinder_verts_top[next_i]])

# Build spiral steps
for step_num in range(num_steps):
    angle_deg = step_num * step_rotation
    angle_rad = math.radians(angle_deg)
    z = step_num * step_height
    
    # Compute step position
    step_x = step_radius * math.cos(angle_rad)
    step_y = step_radius * math.sin(angle_rad)
    
    # Step corners (tread)
    # Inner edge (closer to center)
    inner_radius = step_radius - step_depth / 2
    inner_x = inner_radius * math.cos(angle_rad)
    inner_y = inner_radius * math.sin(angle_rad)
    
    # Outer edge
    outer_radius = step_radius + step_depth / 2
    outer_x = outer_radius * math.cos(angle_rad)
    outer_y = outer_radius * math.sin(angle_rad)
    
    # Left and right edges (perpendicular to radial direction)
    perp_angle = angle_rad + math.pi / 2
    left_offset_x = (step_width / 2) * math.cos(perp_angle)
    left_offset_y = (step_width / 2) * math.sin(perp_angle)
    right_offset_x = -(step_width / 2) * math.cos(perp_angle)
    right_offset_y = -(step_width / 2) * math.sin(perp_angle)
    
    # Four corners of step tread
    v1 = bm.verts.new((inner_x + left_offset_x, inner_y + left_offset_y, z))
    v2 = bm.verts.new((inner_x + right_offset_x, inner_y + right_offset_y, z))
    v3 = bm.verts.new((outer_x + right_offset_x, outer_y + right_offset_y, z))
    v4 = bm.verts.new((outer_x + left_offset_x, outer_y + left_offset_y, z))
    
    # Top surface of tread
    bm.faces.new([v1, v2, v3, v4])
    
    # Riser (vertical face connecting to previous step)
    if step_num > 0:
        prev_angle_rad = math.radians((step_num - 1) * step_rotation)
        prev_z = (step_num - 1) * step_height
        prev_outer_radius = step_radius + step_depth / 2
        prev_outer_x = prev_outer_radius * math.cos(prev_angle_rad)
        prev_outer_y = prev_outer_radius * math.sin(prev_angle_rad)
        
        prev_perp_angle = prev_angle_rad + math.pi / 2
        prev_left_offset_x = (step_width / 2) * math.cos(prev_perp_angle)
        prev_left_offset_y = (step_width / 2) * math.sin(prev_perp_angle)
        prev_right_offset_x = -(step_width / 2) * math.cos(prev_perp_angle)
        prev_right_offset_y = -(step_width / 2) * math.sin(prev_perp_angle)
        
        pv3 = bm.verts.new((prev_outer_x + prev_right_offset_x, prev_outer_y + prev_right_offset_y, prev_z))
        pv4 = bm.verts.new((prev_outer_x + prev_left_offset_x, prev_outer_y + prev_left_offset_y, prev_z))
        
        bm.faces.new([pv3, v3, v4, pv4])

# Build helical handrail
handrail_segments = num_steps * 4  # More segments for smoother curve
handrail_verts = []

for seg in range(handrail_segments):
    t = seg / handrail_segments
    angle_rad = t * num_steps * math.radians(step_rotation)
    z = t * cylinder_height
    
    x = handrail_radius * math.cos(angle_rad)
    y = handrail_radius * math.sin(angle_rad)
    
    # Create a small circle around the helix for thickness
    circle_verts = []
    num_circle_sides = 6
    for circle_i in range(num_circle_sides):
        circle_angle = (circle_i / num_circle_sides) * 2 * math.pi
        cx = handrail_thickness * math.cos(circle_angle)
        cy = handrail_thickness * math.sin(circle_angle) * 0.5
        
        vx = x + cx * math.cos(angle_rad) - cy * math.sin(angle_rad)
        vy = y + cx * math.sin(angle_rad) + cy * math.cos(angle_rad)
        
        v = bm.verts.new((vx, vy, z + cy * 0.5))
        circle_verts.append(v)
    
    handrail_verts.append(circle_verts)

# Connect handrail segments
for seg in range(handrail_segments - 1):
    current_circle = handrail_verts[seg]
    next_circle = handrail_verts[seg + 1]
    num_circle_sides = len(current_circle)
    
    for circle_i in range(num_circle_sides):
        next_circle_i = (circle_i + 1) % num_circle_sides
        
        v1 = current_circle[circle_i]
        v2 = current_circle[next_circle_i]
        v3 = next_circle[next_circle_i]
        v4 = next_circle[circle_i]
        
        bm.faces.new([v1, v2, v3, v4])

# Finalize mesh
bm.to_mesh(mesh)
bm.free()
mesh.update()

# Smooth shading
for face in mesh.polygons:
    face.use_smooth = True

print(f"Spiral staircase created with {len(mesh.polygons)} faces")
