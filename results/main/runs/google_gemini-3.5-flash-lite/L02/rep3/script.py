import bpy
import bmesh

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_snowman():
    # 1. Body spheres (Bottom, Middle, Head)
    # Using low segment/ring counts to keep the face count well under 3,000
    
    # Bottom sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=16, radius=1.5, location=(0, 0, 1.5)
    )
    bottom_sphere = bpy.context.active_object
    bottom_sphere.name = "Snowman_Bottom"
    
    # Middle sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=14, radius=1.0, location=(0, 0, 3.4)
    )
    middle_sphere = bpy.context.active_object
    middle_sphere.name = "Snowman_Middle"
    
    # Head sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=12, radius=0.6, location=(0, 0, 4.8)
    )
    head_sphere = bpy.context.active_object
    head_sphere.name = "Snowman_Head"
    
    # 2. Carrot Nose (Cone)
    bpy.ops.mesh.primitive_cone_add(
        vertices=12, radius1=0.15, depth=0.8, location=(0, -0.6, 4.85), rotation=(1.5708, 0, 0)
    )
    nose = bpy.context.active_object
    nose.name = "Snowman_Nose"
    
    # 3. Eyes (Small spheres)
    # Left eye
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6, radius=0.08, location=(-0.18, -0.5, 5.0)
    )
    eye_left = bpy.context.active_object
    eye_left.name = "Snowman_Eye_Left"
    
    # Right eye
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=8, ring_count=6, radius=0.08, location=(0.18, -0.5, 5.0)
    )
    eye_right = bpy.context.active_object
    eye_right.name = "Snowman_Eye_Right"

    # Optional: Join all parts into a single snowman object for cleanliness
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [bottom_sphere, middle_sphere, head_sphere, nose, eye_left, eye_right]:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = bottom_sphere
    bpy.ops.object.join()
    
    snowman = bpy.context.active_object
    snowman.name = "Snowman"
    
    # Apply smooth shading to the snowman
    for face in snowman.data.polygons:
        face.use_smooth = True

create_snowman()
