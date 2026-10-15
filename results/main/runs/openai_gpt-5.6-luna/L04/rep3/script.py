import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Material
material = bpy.data.materials.new(name="Pawn Material")
material.diffuse_color = (0.12, 0.16, 0.22, 1.0)
material.metallic = 0.15
material.roughness = 0.28

def apply_material_and_smooth(obj):
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True

# Wide cylindrical base
bpy.ops.mesh.primitive_cylinder_add(
    vertices=48,
    radius=1.25,
    depth=0.34,
    location=(0.0, 0.0, 0.17)
)
base = bpy.context.object
base.name = "Pawn Base"
apply_material_and_smooth(base)

# Tapered body
bpy.ops.mesh.primitive_cone_add(
    vertices=48,
    radius1=0.92,
    radius2=0.56,
    depth=1.55,
    location=(0.0, 0.0, 1.10)
)
body = bpy.context.object
body.name = "Pawn Tapered Body"
apply_material_and_smooth(body)

# Torus collar
bpy.ops.mesh.primitive_torus_add(
    major_segments=48,
    minor_segments=12,
    major_radius=0.57,
    minor_radius=0.13,
    location=(0.0, 0.0, 1.90)
)
collar = bpy.context.object
collar.name = "Pawn Collar"
apply_material_and_smooth(collar)

# Spherical head
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=0.46,
    location=(0.0, 0.0, 2.43)
)
head = bpy.context.object
head.name = "Pawn Head"
apply_material_and_smooth(head)

# Ensure the scene contains no cameras or lights
for obj in list(bpy.data.objects):
    if obj.type in {'CAMERA', 'LIGHT'}:
        bpy.data.objects.remove(obj, do_unlink=True)
