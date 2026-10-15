import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove unused mesh data
for mesh in list(bpy.data.meshes):
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

# Material
mat = bpy.data.materials.new(name="Pawn Material")
mat.diffuse_color = (0.12, 0.16, 0.22, 1.0)
mat.metallic = 0.15
mat.roughness = 0.28

def smooth_object(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.materials.append(mat)

# Wide cylindrical base
bpy.ops.mesh.primitive_cylinder_add(
    vertices=32,
    radius=1.15,
    depth=0.30,
    location=(0.0, 0.0, 0.15)
)
base = bpy.context.object
base.name = "Pawn_Base"
smooth_object(base)

# Tapered pawn body
bpy.ops.mesh.primitive_cone_add(
    vertices=32,
    radius1=0.78,
    radius2=0.40,
    depth=1.25,
    location=(0.0, 0.0, 0.90)
)
body = bpy.context.object
body.name = "Pawn_Tapered_Body"
smooth_object(body)

# Torus collar around the neck
bpy.ops.mesh.primitive_torus_add(
    major_segments=32,
    minor_segments=8,
    mode='MAJOR_MINOR',
    major_radius=0.34,
    minor_radius=0.12,
    location=(0.0, 0.0, 1.53)
)
collar = bpy.context.object
collar.name = "Pawn_Collar"
smooth_object(collar)

# Spherical head
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=0.40,
    location=(0.0, 0.0, 1.90)
)
head = bpy.context.object
head.name = "Pawn_Head"
smooth_object(head)

# Keep transforms applied and ensure all objects are aligned to the Z axis
for obj in (base, body, collar, head):
    obj.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)
