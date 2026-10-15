import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create collection for the pawn parts
# We will use primitive operators which add objects to the active scene in Blender 4.2

# 1. Wide Cylinder Base
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.2,
    depth=0.3,
    vertices=32,
    location=(0, 0, 0.15)
)
base = bpy.context.active_object
base.name = "Pawn_Base"

# 2. Torus Collar (sitting right on top of the base)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.9,
    minor_radius=0.15,
    major_segments=32,
    minor_segments=16,
    location=(0, 0, 0.35)
)
collar = bpy.context.active_object
collar.name = "Pawn_Collar"

# 3. Tapered Cylinder Body (Cone-like with a flat top)
bpy.ops.mesh.primitive_cone_add(
    radius1=0.75,
    radius2=0.4,
    depth=1.5,
    vertices=32,
    location=(0, 0, 1.15)
)
body = bpy.context.active_object
body.name = "Pawn_Body"

# 4. Sphere Head
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=0.5,
    segments=32,
    ring_count=16,
    location=(0, 0, 2.15)
)
head = bpy.context.active_object
head.name = "Pawn_Head"

# Optional: Join them into a single mesh object for cleanliness and correct polycount checking
# Select all created mesh objects
bpy.ops.object.select_all(action='DESELECT')
for obj in [base, collar, body, head]:
    obj.select_set(True)

bpy.context.view_layer.objects.active = base
bpy.ops.object.join()

# Final unified object name and smooth shading
base.name = "Chess_Pawn"
bpy.ops.object.shade_smooth()
