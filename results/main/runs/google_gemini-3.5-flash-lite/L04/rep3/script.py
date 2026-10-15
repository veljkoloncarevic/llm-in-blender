import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_pawn():
    # 1. Wide Cylinder Base
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.2,
        depth=0.3,
        vertices=32,
        location=(0, 0, 0.15)
    )
    base = bpy.context.active_object
    base.name = "Pawn_Base"
    
    # 2. Torus Collar
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.9,
        minor_radius=0.12,
        major_segments=32,
        minor_segments=16,
        location=(0, 0, 0.35)
    )
    collar = bpy.context.active_object
    collar.name = "Pawn_Collar"
    
    # 3. Tapered Cylinder Body
    # Using a cone with a flat top (or adjusted radii)
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.75,
        radius2=0.35,
        depth=1.6,
        vertices=32,
        location=(0, 0, 1.2)
    )
    body = bpy.context.active_object
    body.name = "Pawn_Body"
    
    # 4. Sphere Head
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.55,
        segments=32,
        ring_count=16,
        location=(0, 0, 2.3)
    )
    head = bpy.context.active_object
    head.name = "Pawn_Head"
    
    # Optional: Join them into a single mesh to keep the scene clean and unified
    bpy.ops.object.select_all(action='DESELECT')
    base.select_set(True)
    collar.select_set(True)
    body.select_set(True)
    head.select_set(True)
    
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    
    # Rename the combined object
    base.name = "Chess_Pawn"
    
    # Smooth shading for a polished look
    bpy.ops.object.shade_smooth()

create_pawn()
