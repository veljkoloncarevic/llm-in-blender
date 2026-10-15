import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Helper function to create a primitive with a given location and scale
def create_primitive(type_func, name, location, scale, **kwargs):
    type_func(location=location, **kwargs)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    # Apply scale to keep geometry and modifiers clean
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

# 1. Base: Wide cylinder
# Using lower vertex count to keep total faces under 3,000
base = create_primitive(
    bpy.ops.mesh.primitive_cylinder_add,
    name="Pawn_Base",
    location=(0, 0, 0.1),
    scale=(1.2, 1.2, 0.2),
    vertices=32,
    radius=1.0,
    depth=1.0
)

# 2. Collar: Torus above the base
collar = create_primitive(
    bpy.ops.mesh.primitive_torus_add,
    name="Pawn_Collar",
    location=(0, 0, 0.25),
    scale=(0.85, 0.85, 0.85),
    major_segments=32,
    minor_segments=16,
    major_radius=1.0,
    minor_radius=0.1
)

# 3. Body: Tapered cylinder / cone
body = create_primitive(
    bpy.ops.mesh.primitive_cone_add,
    name="Pawn_Body",
    location=(0, 0, 0.85),
    scale=(0.7, 0.7, 1.0),
    vertices=32,
    radius1=1.0,
    radius2=0.4,
    depth=1.2
)

# 4. Head: Sphere
head = create_primitive(
    bpy.ops.mesh.primitive_uv_sphere_add,
    name="Pawn_Head",
    location=(0, 0, 1.65),
    scale=(0.55, 0.55, 0.55),
    segments=32,
    ring_count=16,
    radius=1.0
)

# Select all parts and join them into a single mesh
bpy.ops.object.select_all(action='DESELECT')
base.select_set(True)
collar.select_set(True)
body.select_set(True)
head.select_set(True)

bpy.context.view_layer.objects.active = base
bpy.ops.object.join()

# Rename the final combined object
pawn = bpy.context.active_object
pawn.name = "Chess_Pawn"

# Smooth shading for a nice classic look
bpy.ops.object.shade_smooth()
