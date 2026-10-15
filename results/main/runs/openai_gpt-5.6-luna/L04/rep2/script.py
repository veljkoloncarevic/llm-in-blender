import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Material
material = bpy.data.materials.new(name="Pawn Material")
material.diffuse_color = (0.16, 0.28, 0.48, 1.0)
material.metallic = 0.15
material.roughness = 0.3

def apply_material(obj):
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True

# Wide cylindrical base
bpy.ops.mesh.primitive_cylinder_add(
    vertices=48,
    radius=1.25,
    depth=0.34,
    end_fill_type='NGON',
    location=(0.0, 0.0, 0.17)
)
base = bpy.context.object
base.name = "Pawn_Base"
apply_material(base)

# Tapered body
bpy.ops.mesh.primitive_cone_add(
    vertices=48,
    radius1=0.98,
    radius2=0.57,
    depth=1.55,
    end_fill_type='NGON',
    location=(0.0, 0.0, 1.10)
)
body = bpy.context.object
body.name = "Pawn_Tapered_Body"
apply_material(body)

# Torus collar
bpy.ops.mesh.primitive_torus_add(
    major_segments=48,
    minor_segments=12,
    location=(0.0, 0.0, 1.86),
    major_radius=0.57,
    minor_radius=0.13
)
collar = bpy.context.object
collar.name = "Pawn_Collar"
apply_material(collar)

# Spherical head
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=32,
    ring_count=16,
    radius=0.43,
    location=(0.0, 0.0, 2.30)
)
head = bpy.context.object
head.name = "Pawn_Head"
apply_material(head)

# Ensure the object transforms and shading are consistent
for obj in (base, body, collar, head):
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.select_set(False)
