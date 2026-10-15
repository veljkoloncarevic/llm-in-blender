import bpy
import bmesh
from mathutils import Vector

# Clear all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a material for the pawn
mat = bpy.data.materials.new(name="PawnMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)

def create_pawn():
    """Create a chess pawn from primitives"""
    
    # 1. Base - Wide cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.8,
        depth=0.3,
        vertices=16,
        location=(0, 0, 0.15)
    )
    base = bpy.context.active_object
    base.name = "Pawn_Base"
    base.data.materials.append(mat)
    
    # 2. Collar - Torus
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.6,
        minor_radius=0.15,
        major_segments=12,
        minor_segments=8,
        location=(0, 0, 0.5)
    )
    collar = bpy.context.active_object
    collar.name = "Pawn_Collar"
    collar.data.materials.append(mat)
    
    # 3. Body - Tapered cylinder (using cone with appropriate parameters)
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.5,
        radius2=0.25,
        depth=1.2,
        vertices=12,
        location=(0, 0, 1.1)
    )
    body = bpy.context.active_object
    body.name = "Pawn_Body"
    body.data.materials.append(mat)
    
    # 4. Head - Sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.35,
        segments=10,
        ring_count=8,
        location=(0, 0, 2.0)
    )
    head = bpy.context.active_object
    head.name = "Pawn_Head"
    head.data.materials.append(mat)
    
    # Join all objects into one mesh
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    collar.select_set(True)
    body.select_set(True)
    head.select_set(True)
    
    bpy.ops.object.join()
    
    pawn = bpy.context.active_object
    pawn.name = "Chess_Pawn"
    
    return pawn

# Create the pawn
pawn = create_pawn()

# Verify face count
face_count = len(pawn.data.polygons)
print(f"Total faces in pawn: {face_count}")
