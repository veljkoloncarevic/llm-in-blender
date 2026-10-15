import bpy
import bmesh
import mathutils

# 1. Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Define the 2D profile points (X, Z) for the vase
# Requirements: flat base, wide body, narrow neck, flared lip
profile_points = [
    (0.0, 0.0),    # Center of base
    (1.2, 0.0),    # Outer edge of flat base
    (1.4, 0.2),    # Lower body curve start
    (2.2, 0.8),    # Widest part of the body
    (1.8, 1.8),    # Upper body tapering in
    (0.7, 2.8),    # Neck tightening
    (0.6, 3.8),    # Narrowest part of the neck
    (1.0, 4.2)     # Flaring lip at the top
]

# 3. Create mesh and object
mesh = bpy.data.meshes.new("VaseMesh")
obj = bpy.data.objects.new("Vase", mesh)
bpy.context.collection.objects.link(obj)

# 4. Use BMesh to lathe/spin the profile around the Z-axis
bm = bmesh.new()

# Convert profile points to Vector3D (Y becomes Z, X stays X, Y is 0 for rotation)
verts = [mathutils.Vector((pt[0], 0.0, pt[1])) for pt in profile_points]

# Create the initial profile edge chain
profile_verts = []
for v_pos in verts:
    profile_verts.append(bm.verts.new(v_pos))

# Revolve the profile around the Z axis
# 32 segments provide a smooth base for subdivision while staying well within the face count limits
steps = 32
angle = mathutils.Matrix.Rotation(2.0 * mathutils.math.pi / steps, 4, 'Z')

current_ring = profile_verts
all_rings = [current_ring]

for _ in range(steps - 1):
    new_ring = []
    for v in current_ring:
        new_v = bm.verts.new(angle @ v.co)
        new_ring.append(new_v)
    
    # Bridge the previous ring and the new ring
    for i in range(len(current_ring) - 1):
        v1 = current_ring[i]
        v2 = current_ring[i+1]
        v3 = new_ring[i+1]
        v4 = new_ring[i]
        bm.faces.new((v1, v2, v3, v4))
        
    current_ring = new_ring
    all_rings.append(current_ring)

# Close the loop between the last ring and the first ring
first_ring = all_rings[0]
last_ring = all_rings[-1]
for i in range(len(first_ring) - 1):
    v1 = last_ring[i]
    v2 = last_ring[i+1]
    v3 = first_ring[i+1]
    v4 = first_ring[i]
    bm.faces.new((v1, v2, v3, v4))

# Cap the bottom center (fan fill from the center point to the first segment ring)
bottom_center_verts = [ring[0] for ring in all_rings]
bm.faces.new(bottom_center_verts)

# Cap the top rim (bridge the inner/outer lip if needed, or just leave open / solidify)
# For a hollow vase look, we can cap the top edge loop between the inner-most and outer-most top verts, 
# but a simple open top with a Solidify modifier yields a much better vase topology.
bm.to_mesh(mesh)
bm.free()

# 5. Set smooth shading for all faces
for p in mesh.polygons:
    p.use_smooth = True

# 6. Add Modifiers for thickness and high-poly smoothness
# Solidify gives the vase physical wall thickness
solidify_mod = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify_mod.thickness = 0.08
solidify_mod.offset = 1.0

# Subsurf for high fidelity and smooth organic look
subsurf_mod = obj.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf_mod.levels = 2
subsurf_mod.render_levels = 2

# Select the object
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
