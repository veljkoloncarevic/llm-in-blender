import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Parameters
num_steps = 24
step_rotation = 15  # degrees per step
step_height = 0.3  # height increase per step
column_radius = 0.5
column_height = num_steps * step_height + 1
step_depth = 1.2  # depth of each step
step_width = 2.0  # width of each step
handrail_radius = step_depth + column_radius + 0.1  # outer radius for handrail
handrail_thickness = 0.05

# Create central column (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=column_radius,
    depth=column_height,
    vertices=32,
    location=(0, 0, column_height / 2)
)
column = bpy.context.active_object
column.name = "Column"

# Create steps
steps_mesh = bpy.data.meshes.new("StairsMesh")
steps_obj = bpy.data.objects.new("Stairs", steps_mesh)
bpy.context.collection.objects.link(steps_obj)
bpy.context.view_layer.objects.active = steps_obj
steps_obj.select_set(True)

bm = bmesh.new()

# Generate step geometry
for i in range(num_steps):
    angle = math.radians(i * step_rotation)
    next_angle = math.radians((i + 1) * step_rotation)
    height = i * step_height
    next_height = (i + 1) * step_height
    
    # Inner edge of step (closer to column)
    inner_radius = column_radius + 0.1
    
    # Outer edge of step
    outer_radius = column_radius + step_depth
    
    # Create vertices for this step (a rectangular section)
    # Current step level - inner front
    v0 = bm.verts.new((
        inner_radius * math.cos(angle),
        inner_radius * math.sin(angle),
        height
    ))
    # Current step level - inner back
    v1 = bm.verts.new((
        inner_radius * math.cos(next_angle),
        inner_radius * math.sin(next_angle),
        height
    ))
    # Current step level - outer front
    v2 = bm.verts.new((
        outer_radius * math.cos(angle),
        outer_radius * math.sin(angle),
        height
    ))
    # Current step level - outer back
    v3 = bm.verts.new((
        outer_radius * math.cos(next_angle),
        outer_radius * math.sin(next_angle),
        height
    ))
    
    # Next step level - inner front
    v4 = bm.verts.new((
        inner_radius * math.cos(next_angle),
        inner_radius * math.sin(next_angle),
        next_height
    ))
    # Next step level - outer front
    v5 = bm.verts.new((
        outer_radius * math.cos(next_angle),
        outer_radius * math.sin(next_angle),
        next_height
    ))
    
    # Create faces for step top surface
    bm.faces.new([v0, v2, v3, v1])
    
    # Create faces for step sides
    bm.faces.new([v1, v3, v5, v4])  # outer edge
    bm.faces.new([v0, v1, v4])  # inner edge (riser)
    bm.faces.new([v2, v5, v3])  # front edge

bm.to_mesh(steps_mesh)
bm.free()
steps_mesh.update()

# Create handrail (helical curve approximated with cylinders)
handrail_mesh = bpy.data.meshes.new("HandrailMesh")
handrail_obj = bpy.data.objects.new("Handrail", handrail_mesh)
bpy.context.collection.objects.link(handrail_obj)
bpy.context.view_layer.objects.active = handrail_obj
handrail_obj.select_set(True)

bm = bmesh.new()

# Create handrail as a series of connected torus segments
handrail_segments = num_steps * 4
for i in range(handrail_segments):
    angle = math.radians(i * 360 / handrail_segments)
    next_angle = math.radians((i + 1) * 360 / handrail_segments)
    height = (i / handrail_segments) * num_steps * step_height
    next_height = ((i + 1) / handrail_segments) * num_steps * step_height
    
    # Create small tube segment
    segments = 8
    for j in range(segments):
        seg_angle = math.radians(j * 360 / segments)
        next_seg_angle = math.radians((j + 1) * 360 / segments)
        
        # Current position on helix
        x1 = handrail_radius * math.cos(angle)
        y1 = handrail_radius * math.sin(angle)
        
        # Next position on helix
        x2 = handrail_radius * math.cos(next_angle)
        y2 = handrail_radius * math.sin(next_angle)
        
        # Create vertices around the tube
        v_list = []
        for k in range(4):
            t = k / 3.0
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            z = height + (next_height - height) * t
            
            vx = x + handrail_thickness * math.cos(seg_angle)
            vy = y + handrail_thickness * math.sin(seg_angle)
            
            v = bm.verts.new((vx, vy, z))
            v_list.append(v)
        
        # Create connecting faces
        if i > 0 or j > 0:
            if len(bm.verts) >= 4:
                recent_verts = list(bm.verts)[-8:-4]
                if len(recent_verts) == 4:
                    try:
                        bm.faces.new([v_list[0], v_list[1], recent_verts[1], recent_verts[0]])
                        bm.faces.new([v_list[1], v_list[2], recent_verts[2], recent_verts[1]])
                        bm.faces.new([v_list[2], v_list[3], recent_verts[3], recent_verts[2]])
                    except:
                        pass

bm.to_mesh(handrail_mesh)
bm.free()
handrail_mesh.update()

# Set smooth shading
for obj in [steps_obj, handrail_obj, column]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
