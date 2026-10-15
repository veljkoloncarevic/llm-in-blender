import math
import bpy
import bmesh

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the spur gear
num_teeth = 24
module = 0.5  # Controls gear size
thickness = 0.3
hole_radius = 0.8

# Calculated gear dimensions
pitch_radius = (num_teeth * module) / 2.0
addendum = module
dedendum = 1.25 * module
outer_radius = pitch_radius + addendum
root_radius = pitch_radius - dedendum

# Create mesh and bmesh
mesh = bpy.data.meshes.new("SpurGearMesh")
obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Resolution per tooth
steps_per_tooth = 8
total_steps = num_teeth * steps_per_tooth
angle_step = (2 * math.pi) / total_steps

front_verts = []
back_verts = []
hole_front_verts = []
hole_back_verts = []

# Hole resolution matches total steps for easy bridging
hole_res = total_steps
for i in range(hole_res):
    angle = i * (2 * math.pi / hole_res)
    x = math.cos(angle) * hole_radius
    y = math.sin(angle) * hole_radius
    
    v_front = bm.verts.new((x, y, thickness / 2.0))
    v_back = bm.verts.new((x, y, -thickness / 2.0))
    
    hole_front_verts.append(v_front)
    hole_back_verts.append(v_back)

# Generate gear outer profile vertices
for i in range(total_steps):
    theta = i * angle_step
    # Approximate involute-like profile using sine wave modulation
    # Crests for teeth, troughs for roots
    tooth_mod = math.sin(theta * num_teeth)
    
    if tooth_mod > 0:
        # Interpolate towards outer radius at the tip
        r = root_radius + (outer_radius - root_radius) * (tooth_mod ** 0.5)
    else:
        # Root circle
        r = root_radius

    x = math.cos(theta) * r
    y = math.sin(theta) * r
    
    vf = bm.verts.new((x, y, thickness / 2.0))
    vb = bm.verts.new((x, y, -thickness / 2.0))
    
    front_verts.append(vf)
    back_verts.append(vb)

bm.verts.ensure_lookup_table()

# Create front face (N-gon with hole)
# BMesh handles faces with internal loops if we construct properly, 
# but an easier robust way is to create quad strips between hole and outer profile.
# Since hole_res == total_steps, we can stitch them directly with quads!

for i in range(total_steps):
    next_i = (i + 1) % total_steps
    
    # Indices
    f_in_curr = hole_front_verts[i]
    f_in_next = hole_front_verts[next_i]
    f_out_next = front_verts[next_i]
    f_out_curr = front_verts[i]
    
    # Front face quad (bridging hole to outer)
    bm.faces.new([f_in_curr, f_in_next, f_out_next, f_out_curr])
    
    # Back face quad (reversed winding)
    b_in_curr = hole_back_verts[i]
    b_in_next = hole_back_verts[next_i]
    b_out_next = back_verts[next_i]
    b_out_curr = back_verts[i]
    
    bm.faces.new([b_in_curr, b_out_curr, b_out_next, b_in_next])

# Create outer rim (thickness extrusion)
for i in range(total_steps):
    next_i = (i + 1) % total_steps
    
    f_curr = front_verts[i]
    f_next = front_verts[next_i]
    b_next = back_verts[next_i]
    b_curr = back_verts[i]
    
    bm.faces.new([f_curr, f_next, b_next, b_curr])

# Create inner hole wall
for i in range(hole_res):
    next_i = (i + 1) % hole_res
    
    f_curr = hole_front_verts[i]
    f_next = hole_front_verts[next_i]
    b_next = hole_back_verts[next_i]
    b_curr = hole_back_verts[i]
    
    # Reversed for inner wall normals pointing inward/outward correctly
    bm.faces.new([f_curr, b_curr, b_next, f_next])

# Finish up bmesh and update object
bm.normal_update()
bm.to_mesh(mesh)
bm.free()

# Set smooth shading for a clean look
for poly in mesh.polygons:
    poly.use_smooth = True

# Select the object
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
