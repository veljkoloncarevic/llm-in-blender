import bpy
import bmesh
import math
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
num_steps = 24
step_height = 0.3
step_depth = 0.4
step_width = 2.0
angle_per_step = math.radians(15)
radius_inner = 0.5  # Inner cylinder radius
radius_outer = radius_inner + step_width

# Create central column (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=radius_inner,
    depth=num_steps * step_height,
    vertices=16,
    location=(0, 0, num_steps * step_height / 2)
)
column = bpy.context.active_object
column.name = "Column"

# Create staircase mesh
stair_mesh = bpy.data.meshes.new("StaircaseMesh")
stair_obj = bpy.data.objects.new("Staircase", stair_mesh)
bpy.context.collection.objects.link(stair_obj)
bpy.context.view_layer.objects.active = stair_obj
stair_obj.select_set(True)

bm = bmesh.new()

# Build steps
for step_idx in range(num_steps):
    angle = step_idx * angle_per_step
    next_angle = (step_idx + 1) * angle_per_step
    z = step_idx * step_height
    z_next = (step_idx + 1) * step_height
    
    # Current step corners
    p1 = Vector((radius_inner * math.cos(angle), radius_inner * math.sin(angle), z))
    p2 = Vector((radius_outer * math.cos(angle), radius_outer * math.sin(angle), z))
    p3 = Vector((radius_outer * math.cos(next_angle), radius_outer * math.sin(next_angle), z))
    p4 = Vector((radius_inner * math.cos(next_angle), radius_inner * math.sin(next_angle), z))
    
    # Next step corners
    p5 = Vector((radius_inner * math.cos(angle), radius_inner * math.sin(angle), z_next))
    p6 = Vector((radius_outer * math.cos(angle), radius_outer * math.sin(angle), z_next))
    p7 = Vector((radius_outer * math.cos(next_angle), radius_outer * math.sin(next_angle), z_next))
    p8 = Vector((radius_inner * math.cos(next_angle), radius_inner * math.sin(next_angle), z_next))
    
    # Add vertices
    v1 = bm.verts.new(p1)
    v2 = bm.verts.new(p2)
    v3 = bm.verts.new(p3)
    v4 = bm.verts.new(p4)
    v5 = bm.verts.new(p5)
    v6 = bm.verts.new(p6)
    v7 = bm.verts.new(p7)
    v8 = bm.verts.new(p8)
    
    # Top surface (tread)
    bm.faces.new([v5, v6, v7, v8])
    
    # Outer edge
    bm.faces.new([v2, v3, v7, v6])
    
    # Inner edge
    bm.faces.new([v1, v5, v8, v4])
    
    # Front face (riser)
    bm.faces.new([v1, v4, v3, v2])
    
    # Back face
    bm.faces.new([v4, v8, v7, v3])

# Create handrail (helical curve approximated with segments)
handrail_radius = radius_outer + 0.15
handrail_height = 0.08
handrail_segments = num_steps * 4

for seg_idx in range(handrail_segments):
    t = seg_idx / handrail_segments
    angle = t * num_steps * angle_per_step
    z = t * num_steps * step_height
    
    # Create a small torus segment for handrail
    center = Vector((handrail_radius * math.cos(angle), handrail_radius * math.sin(angle), z))
    
    # Next segment
    t_next = (seg_idx + 1) / handrail_segments
    angle_next = t_next * num_steps * angle_per_step
    z_next = t_next * num_steps * step_height
    center_next = Vector((handrail_radius * math.cos(angle_next), handrail_radius * math.sin(angle_next), z_next))
    
    # Create vertices around the handrail cross-section
    for i in range(8):
        theta = (i / 8) * 2 * math.pi
        offset = Vector((
            0.08 * math.cos(theta) * math.cos(angle),
            0.08 * math.cos(theta) * math.sin(angle),
            0.08 * math.sin(theta)
        ))
        v = bm.verts.new(center + offset)

# Ensure lookup table is built
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# Write bmesh to mesh
bm.to_mesh(stair_mesh)
bm.free()

# Update mesh
stair_mesh.update()

# Add smooth shading
bpy.context.view_layer.objects.active = stair_obj
bpy.ops.object.shade_smooth()

print(f"Staircase created with {len(stair_mesh.vertices)} vertices and {len(stair_mesh.polygons)} faces")
