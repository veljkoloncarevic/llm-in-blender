import bpy

# Remove existing objects
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
if bpy.context.selected_objects:
    bpy.ops.object.delete(use_global=False)

parts = []

# Base cylinder
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.6, depth=0.15, location=(0, 0, 0.075))
parts.append(bpy.context.active_object)

# Collar torus
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.42, minor_radius=0.05,
    major_segments=16, minor_segments=8,
    location=(0, 0, 0.28)
)
parts.append(bpy.context.active_object)

# Tapered body (cone)
bpy.ops.mesh.primitive_cone_add(
    vertices=16, radius1=0.4, radius2=0.2, depth=0.8,
    location=(0, 0, 0.15)
)
parts.append(bpy.context.active_object)

# Head sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=12, ring_count=8, radius=0.28,
    location=(0, 0, 1.18)
)
parts.append(bpy.context.active_object)

# Join all parts into a single object
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
bpy.context.active_object.name = "ChessPawn"
