import bpy
import bmesh
from mathutils import Vector

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a material for the pawn
mat = bpy.data.materials.new(name="PawnMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)

def create_pawn():
    """Create a chess pawn from primitives"""
    
    # 1. Base cylinder (wide and short)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.5,
        depth=0.3,
        vertices=16,
        location=(0, 0, 0.15)
    )
    base = bpy.context.active_object
    base.data.materials.append(mat)
    base.name = "PawnBase"
    
    # 2. Torus collar
    bpy.ops.mesh.primitive_torus_add(
        location=(0, 0, 0.45),
        major_radius=0.35,
        minor_radius=0.08,
        major_segments=12,
        minor_segments=6
    )
    collar = bpy.context.active_object
    collar.data.materials.append(mat)
    collar.name = "PawnCollar"
    
    # 3. Tapered body (cone)
    bpy.ops.mesh.primitive_cone_add(
        radius1=0.3,
        radius2=0.15,
        depth=0.8,
        vertices=12,
        location=(0, 0, 1.0)
    )
    body = bpy.context.active_object
    body.data.materials.append(mat)
    body.name = "PawnBody"
    
    # 4. Head sphere
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.2,
        location=(0, 0, 1.6),
        segments=12,
        rings=8
    )
    head = bpy.context.active_object
    head.data.materials.append(mat)
    head.name = "PawnHead"
    
    # Join all parts into a single object
    bpy.context.view_layer.objects.active = base
    base.select_set(True)
    collar.select_set(True)
    body.select_set(True)
    head.select_set(True)
    
    bpy.ops.object.join()
    
    pawn = bpy.context.active_object
    pawn.name = "ChessPawn"
    
    return pawn

# Create the pawn
pawn = create_pawn()

# Verify face count
mesh = pawn.data
face_count = len(mesh.polygons)
print(f"Pawn created with {face_count} faces")
