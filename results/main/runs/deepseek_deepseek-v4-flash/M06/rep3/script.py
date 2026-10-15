import bpy
import bmesh
import math

# Remove all existing objects
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gear parameters
num_teeth = 24
thickness = 0.3
outer_radius = 2.5
root_radius = 2.0
hole_radius = 0.8

pitch = 2.0 * math.pi / num_teeth
half_tip = 0.25 * pitch

# Build angle list for one tooth: root, tip start, tip end
angles = []
for i in range(num_teeth):
    a = i * pitch
    angles.append(a - 0.5 * pitch)   # root point before the tooth
    angles.append(a - half_tip)      # tip leading edge
    angles.append(a + half_tip)      # tip trailing edge

# Create bmesh
bm = bmesh.new()

outer_top = []
outer_bot = []
inner_top = []
inner_bot = []

z_top = thickness / 2.0
z_bot = -thickness / 2.0

for a in angles:
    c = math.cos(a)
    s = math.sin(a)

    # Outer ring
    outer_top.append(bm.verts.new((outer_radius * c, outer_radius * s, z_top)))
    outer_bot.append(bm.verts.new((outer_radius * c, outer_radius * s, z_bot)))

    # Inner hole ring
    inner_top.append(bm.verts.new((hole_radius * c, hole_radius * s, z_top)))
    inner_bot.append(bm.verts.new((hole_radius * c, hole_radius * s, z_bot)))

n = len(angles)

# Outer side faces (normals outward)
for i in range(n):
    j = (i + 1) % n
    bm.faces.new((outer_top[i], outer_bot[i], outer_bot[j], outer_top[j]))

# Inner hole side faces (normals inward)
for i in range(n):
    j = (i + 1) % n
    bm.faces.new((inner_bot[i], inner_top[i], inner_top[j], inner_bot[j]))

# Top annular face (normal +Z)
for i in range(n):
    j = (i + 1) % n
    bm.faces.new((outer_top[i], outer_top[j], inner_top[j], inner_top[i]))

# Bottom annular face (normal -Z)
for i in range(n):
    j = (i + 1) % n
    bm.faces.new((outer_bot[i], inner_bot[i], inner_bot[j], outer_bot[j]))

# Ensure consistent outward orientation
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Build mesh object
mesh = bpy.data.meshes.new("SpurGear")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.scene.collection.objects.link(obj)
