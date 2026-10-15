import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create trunk: cylinder with 8 sides
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.3,
    depth=2,
    location=(0, 0, 1)
)
trunk = bpy.context.active_object
trunk.name = "Trunk"

# Create canopy: icosphere with 2 subdivisions
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.5,
    location=(0, 0, 2.5)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"
