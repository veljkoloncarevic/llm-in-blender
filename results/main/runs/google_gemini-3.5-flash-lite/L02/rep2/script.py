import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Helper function to create primitives with low poly count to keep under 3000 faces
def create_low_poly_sphere(name, location, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, 
        ring_count=12, 
        radius=1.0, 
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    # Apply scale to keep transformations clean
    bpy.ops.object.transform_apply(scale=True)
    return obj

def create_low_poly_cone(name, location, rotation, scale):
    bpy.ops.mesh.primitive_cone_add(
        vertices=12,
        radius1=1.0,
        depth=2.0,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return obj

# 1. Bottom body sphere (Largest)
body_bottom = create_low_poly_sphere(
    name="Snowman_Body_Bottom",
    location=(0, 0, 1.0),
    scale=(1.5, 1.5, 1.5)
)

# 2. Middle body sphere (Medium)
body_middle = create_low_poly_sphere(
    name="Snowman_Body_Middle",
    location=(0, 0, 3.2),
    scale=(1.05, 1.05, 1.05)
)

# 3. Head sphere (Smallest)
head = create_low_poly_sphere(
    name="Snowman_Head",
    location=(0, 0, 4.7),
    scale=(0.7, 0.7, 0.7)
)

# 4. Carrot nose (Cone)
# Pointing forward (-Y direction in Blender, so rotate accordingly)
import math
nose = create_low_poly_cone(
    name="Snowman_Nose",
    location=(0, -0.65, 4.7),
    rotation=(math.radians(90), 0, 0),
    scale=(0.15, 0.15, 0.5)
)

# 5. Eyes (Two small spheres)
eye_left = create_low_poly_sphere(
    name="Snowman_Eye_Left",
    location=(-0.2, -0.55, 4.9),
    scale=(0.08, 0.08, 0.08)
)

eye_right = create_low_poly_sphere(
    name="Snowman_Eye_Right",
    location=(0.2, -0.55, 4.9),
    scale=(0.08, 0.08, 0.08)
)

# Select all snowman parts and join them into a single mesh object (optional, but keeps outliner clean)
bpy.ops.object.select_all(action='DESELECT')
for obj in [body_bottom, body_middle, head, nose, eye_left, eye_right]:
    obj.select_set(True)

bpy.context.view_layer.objects.active = body_bottom
bpy.ops.object.join()

# Final active object rename
final_snowman = bpy.context.active_object
final_snowman.name = "Snowman"

# Shade smooth across the snowman
bpy.ops.object.shade_smooth()
