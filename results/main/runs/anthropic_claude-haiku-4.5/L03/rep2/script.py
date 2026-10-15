import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create trunk (8-sided cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.3,
    depth=2.0,
    location=(0, 0, 1.0)
)
trunk = bpy.context.active_object
trunk.name = "Trunk"

# Create canopy (icosphere with 1 subdivision for low-poly)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.5,
    location=(0, 0, 3.0)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"

# Delete the default sphere and create icosphere instead
bpy.ops.object.delete(use_global=False)

# Create icosphere with 1 subdivision
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=1,
    radius=1.5,
    location=(0, 0, 3.0)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"

# Verify face counts
trunk_obj = bpy.data.objects["Trunk"]
canopy_obj = bpy.data.objects["Canopy"]

trunk_data = trunk_obj.data
canopy_data = canopy_obj.data

trunk_faces = len(trunk_data.polygons)
canopy_faces = len(canopy_data.polygons)
total_faces = trunk_faces + canopy_faces

# If total is still too high, reduce canopy subdivisions further by using a simpler approach
if total_faces > 400:
    # Remove canopy and create a simpler one
    bpy.data.objects.remove(canopy_obj, do_unlink=True)
    
    # Create icosphere with 0 subdivisions (12 faces)
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=0,
        radius=1.5,
        location=(0, 0, 3.0)
    )
    canopy = bpy.context.active_object
    canopy.name = "Canopy"

# Apply smooth shading for better appearance
for obj in [trunk_obj, canopy]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()

# Final verification
trunk_faces = len(bpy.data.objects["Trunk"].data.polygons)
canopy_faces = len(bpy.data.objects["Canopy"].data.polygons)
total_faces = trunk_faces + canopy_faces
