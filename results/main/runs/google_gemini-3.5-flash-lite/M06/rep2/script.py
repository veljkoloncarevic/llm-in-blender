import math
import bpy
import bmesh

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters for the spur gear
num_teeth = 24
module = 0.5  # Controls size
thickness = 0.3
hole_radius = 1.0

# Gear geometry calculations
pitch_radius = (num_teeth * module) / 2.0
addendum = module
dedendum = 1.25 * module

ra = pitch_radius + addendum       # Tip radius
rd = pitch_radius - dedendum       # Root radius
rb = pitch_radius * math.cos(math.radians(20))  # Base radius (20 deg pressure angle)

# Resolution per tooth
steps_per_tooth = 8
total_steps = num_teeth * steps_per_tooth

# Create BMesh
bm = bmesh.new()

# Helper to generate involute profile points for one tooth interval
def generate_tooth_profile(tooth_idx):
    profile_verts = []
    angle_step = (2.0 * math.pi) / total_steps
    start_step = tooth_idx * steps_per_tooth
    
    for s in range(steps_per_tooth + 1):
        step_idx = start_step + s
        theta = step_idx * angle_step
        
        # Approximate profile using radial interpolation between root and tip
        # modulated by a cosine wave to simulate gear teeth shape
        t = s / float(steps_per_tooth)
        # Tooth shape curve: center of tooth is at t = 0.5
        tooth_local = (t - 0.5) * 2.0  # -1 to 1
        
        # Width modulation (cosine creates the tooth/space profile)
        width_mod = math.cos(tooth_local * math.pi * 0.5)
        
        if abs(tooth_local) <= 0.8:
            r = rd + (ra - rd) * abs(width_mod)
        else:
            r = rd  # Root fillet area
            
        profile_verts.append((math.cos(theta) * r, math.sin(theta) * r))
        
    return profile_verts

# Build outer perimeter vertices (front face)
outer_verts_front = []
outer_verts_back = []
hole_verts_front = []
hole_verts_back = []

angle_step = (2.0 * math.pi) / total_steps

# Generate hole and outer boundary vertices
for i in range(total_steps):
    theta = i * angle_step
    
    # Outer radius modulation for teeth
    t = (i % steps_per_tooth) / float(steps_per_tooth)
    tooth_local = (t - 0.5) * 2.0
    width_mod = math.cos(tooth_local * math.pi * 0.5)
    r = rd + (ra - rd) * abs(width_mod) if abs(tooth_local) <= 0.8 else rd
    
    # Front outer
    v_of = bm.verts.new((math.cos(theta) * r, math.sin(theta) * r, thickness / 2.0))
    outer_verts_front.append(v_of)
    
    # Back outer
    v_ob = bm.verts.new((math.cos(theta) * r, math.sin(theta) * r, -thickness / 2.0))
    outer_verts_back.append(v_ob)
    
    # Front hole
    v_hf = bm.verts.new((math.cos(theta) * hole_radius, math.sin(theta) * hole_radius, thickness / 2.0))
    hole_verts_front.append(v_hf)
    
    # Back hole
    v_hb = bm.verts.new((math.cos(theta) * hole_radius, math.sin(theta) * hole_radius, -thickness / 2.0))
    hole_verts_back.append(v_hb)

# Helper to create a face safely
def safe_face(verts):
    try:
        return bm.faces.new(verts)
    except ValueError:
        # Handle potential duplicate/degenerate if any
        pass

# 1. Outer lateral walls (Quad strip)
for i in range(total_steps):
    nxt = (i + 1) % total_steps
    v1 = outer_verts_front[i]
    v2 = outer_verts_front[nxt]
    v3 = outer_verts_back[nxt]
    v4 = outer_verts_back[i]
    safe_face([v1, v2, v3, v4])

# 2. Inner hole walls (Quad strip - reversed normal)
for i in range(total_steps):
    nxt = (i + 1) % total_steps
    v1 = hole_verts_front[i]
    v2 = hole_verts_back[i]
    v3 = hole_verts_back[nxt]
    v4 = hole_verts_front[nxt]
    safe_face([v1, v2, v3, v4])

# 3. Front and Back caps (Bridge between hole and outer perimeter using BMesh loops)
# We can use bmesh operations to construct the capped planar faces with holes
bm.verts.ensure_lookup_table()

# Collect loops for face creation
front_loop_outer = list(reversed(outer_verts_front))
front_loop_hole = hole_verts_front
safe_face(front_loop_outer + front_loop_hole)

back_loop_outer = outer_verts_back
back_loop_hole = list(reversed(hole_verts_back))
safe_face(back_loop_outer + back_loop_hole)

# Finalize mesh
mesh = bpy.data.meshes.new("SpurGearMesh")
bm.to_mesh(mesh)
bm.free()

# Create object and link to scene
obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(obj)

# Set smooth shading for the cylindrical walls for visual appeal
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()
