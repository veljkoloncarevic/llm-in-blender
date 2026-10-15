import bpy
import bmesh
import mathutils

# Remove all existing objects
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Trunk: 8-sided cylinder
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.35,
    depth=2.0,
    location=(0, 0, 1)
)
trunk = bpy.context.object
trunk.name = "Tree_Trunk"

# Canopy: icosphere with 2 subdivisions, squashed for stylised look
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.0,
    location=(0, 0, 2.5),
    scale=(1.5, 1.5, 1.0)
)
canopy = bpy.context.object
canopy.name = "Tree_Canopy"

# Safety check: keep scene under 400 faces
total_faces = sum(len(obj.data.polygons) for obj in bpy.data.objects if obj.type == 'MESH')
assert total_faces < 400, f"Too many faces: {total_faces}"
