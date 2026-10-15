import bpy
import bmesh
import mathutils
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 1. Create the Mug Body (Cylinder with Solidify)
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.2,
    vertices=32,
    location=(0, 0, 1.1)
)
mug_obj = bpy.context.active_object
mug_obj.name = "CoffeeMug"

# Shade smooth
for poly in mug_obj.data.polygons:
    poly.use_smooth = True

# Add Solidify modifier to make it hollow
solidify_mod = mug_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify_mod.thickness = 0.12
solidify_mod.offset = -1.0 # Thicken inward
solidify_mod.use_rim = True

# 2. Create the Handle (Modified Torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.12,
    major_segments=32,
    minor_segments=16,
    major_arc=math.pi,  # Half torus (180 degrees)
    location=(1.0, 0, 1.1),
    rotation=(0, math.pi/2, 0)
)
handle_obj = bpy.context.active_object
handle_obj.name = "MugHandle"

# Shade smooth for handle
for poly in handle_obj.data.polygons:
    poly.use_smooth = True

# 3. Join Mug and Handle into a single object
bpy.ops.object.select_all(action='DESELECT')
mug_obj.select_set(True)
handle_obj.select_set(True)
bpy.context.view_layer.objects.active = mug_obj
bpy.ops.object.join()

# Final clean-up and positioning at world origin
mug_obj.location = (0, 0, 0)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Select the final object
mug_obj.select_set(True)
