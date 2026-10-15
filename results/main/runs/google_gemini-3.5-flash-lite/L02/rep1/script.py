import bpy
import bmesh
from mathutils import Vector

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Helper function to create a primitive with low polygon count to keep faces under 3,000
def create_low_poly_sphere(location, radius, segments=16, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=radius,
        location=location
    )
    obj = bpy.active_object
    return obj

def create_low_poly_cone(location, radius1, radius2, depth, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(
        vertices=16,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.active_object
    return obj

# 1. Snowman Body - Three stacked UV spheres of decreasing size
# Bottom sphere (Large)
bottom_radius = 1.5
bottom_loc = Vector((0, 0, bottom_radius))
bottom_sphere = create_low_poly_sphere(bottom_loc, bottom_radius, segments=24, rings=24)

# Middle sphere (Medium)
middle_radius = 1.0
# Calculate Z position so it sits nicely on top of the bottom sphere
middle_loc = Vector((0, 0, (bottom_radius * 2) + (middle_radius * 0.8)))
middle_sphere = create_low_poly_sphere(middle_loc, middle_radius, segments=20, rings=20)

# Top sphere (Head - Small)
top_radius = 0.6
top_loc = Vector((0, 0, bottom_loc.z + bottom_radius + (middle_radius * 2 * 0.8) + (top_radius * 0.8)))
top_sphere = create_low_poly_sphere(top_loc, top_radius, segments=16, rings=16)


# 2. Carrot Nose - A cone
# Positioned at the front of the head sphere (positive Y-axis)
nose_radius = 0.12
nose_depth = 0.6
# Rotate to point outwards along the Y-axis (Cone default points along Z)
nose_rot = (1.57079, 0, 0) # 90 degrees in radians on X
nose_loc = Vector((0, top_loc.y + top_radius * 0.8, top_loc.z))
nose = create_low_poly_cone(nose_loc, nose_radius, 0.0, nose_depth, rotation=nose_rot)


# 3. Eyes - Two small spheres
eye_radius = 0.06
eye_z_offset = 0.15
eye_y_offset = 0.5
eye_x_spacing = 0.18

# Left Eye
left_eye_loc = Vector((-eye_x_spacing, top_loc.y + (top_radius * eye_y_offset), top_loc.z + eye_z_offset))
left_eye = create_low_poly_sphere(left_eye_loc, eye_radius, segments=8, rings=8)

# Right Eye
right_eye_loc = Vector((eye_x_spacing, top_loc.y + (top_radius * eye_y_offset), top_loc.z + eye_z_offset))
right_eye = create_low_poly_sphere(right_eye_loc, eye_radius, segments=8, rings=8)


# Optional: Join all objects into a single snowman mesh to ensure clean hierarchy, 
# or keep them separate as per "three stacked... a cone... two small spheres". 
# The prompt implies individual primitive elements modeled together. We'll leave them as separate objects.

# Ensure smooth shading for spheres for a better snowman look
for obj in [bottom_sphere, middle_sphere, top_sphere, left_eye, right_eye]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

# Shade smooth for the cone (nose) as well, but with auto smooth if needed (standard smooth is fine here)
bpy.context.view_layer.objects.active = nose
bpy.ops.object.shade_smooth()

# Final selection clear
bpy.ops.object.select_all(action='DESELECT')
