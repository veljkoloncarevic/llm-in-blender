import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the low-poly trunk (8-sided cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.3,
    depth=2.0,
    location=(0.0, 0.0, 0.0)
)
trunk = bpy.context.active_object
trunk.name = "Trunk"

# Create the low-poly canopy (icosphere, 2 subdivisions)
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.2,
    location=(0.0, 0.0, 2.0)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"
