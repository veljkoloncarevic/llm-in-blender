import bpy
import bmesh
import math

# Remove all existing objects
if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Gear parameters
num_teeth = 24
thickness = 0.3
outer_radius = 1.0
root_radius = 0.8
hole_radius = 0.3
samples_per_tooth = 12
total_samples = num_teeth * samples_per_tooth

pitch = 2.0 * math.pi / num_teeth
tip_half_angle = 0.20 * pitch
root_half_angle = 0.45 * pitch

def gear_radius(theta):
    center_angle = round(theta / pitch) * pitch
    delta = theta - center_angle
    half_pitch = pitch * 0.5

    if delta > half_pitch:
        delta -= pitch
    elif delta < -half_pitch:
        delta += pitch

    abs_delta = abs(delta)

    if abs_delta <= tip_half_angle:
        return outer_radius
    elif abs_delta >= root_half_angle:
        return root_radius
    else:
        t = (abs_delta - tip_half_angle) / (root_half_angle - tip_half_angle)
        return outer_radius + (root_radius - outer_radius) * t

# Build mesh
mesh = bpy.data.meshes.new("SpurGear")
bm = bmesh.new()

outer_bot = [None] * total_samples
inner_bot = [None] * total_samples
outer_top = [None] * total_samples
inner_top = [None] * total_samples

for i in range(total_samples):
    theta = i * (2.0 * math.pi) / total_samples
    r_outer = gear_radius(theta)
    r_inner = hole_radius

    xo = r_outer * math.cos(theta)
    yo = r_outer * math.sin(theta)
    xi = r_inner * math.cos(theta)
    yi = r_inner * math.sin(theta)

    outer_bot[i] = bm.verts.new((xo, yo, 0.0))
    inner_bot[i] = bm.verts.new((xi, yi, 0.0))
    outer_top[i] = bm.verts.new((xo, yo, thickness))
    inner_top[i] = bm.verts.new((xi, yi, thickness))

for i in range(total_samples):
    j = (i + 1) % total_samples

    # Bottom face (normal -Z)
    bm.faces.new((outer_bot[i], inner_bot[i], inner_bot[j], outer_bot[j]))

    # Top face (normal +Z)
    bm.faces.new((outer_top[i], outer_top[j], inner_top[j], inner_top[i]))

    # Outer side face
    bm.faces.new((outer_bot[i], outer_bot[j], outer_top[j], outer_top[i]))

    # Inner side face
    bm.faces.new((inner_bot[i], inner_top[i], inner_top[j], inner_bot[j]))

# Recalculate normals to ensure correct outward orientation
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

# Link mesh as an object
gear_obj = bpy.data.objects.new("SpurGear", mesh)
bpy.context.collection.objects.link(gear_obj)
bpy.context.view_layer.objects.active = gear_obj
gear_obj.select_set(True)
