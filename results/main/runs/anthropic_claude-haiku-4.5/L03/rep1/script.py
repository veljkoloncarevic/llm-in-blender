import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create trunk - cylinder with 8 sides
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.3,
    depth=2.0,
    location=(0, 0, 1)
)
trunk = bpy.context.active_object
trunk.name = "Trunk"

# Create canopy - icosphere with 1 subdivision (2 subdivisions would exceed face budget)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.5,
    location=(0, 0, 3.5)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"

# Convert sphere to icosphere by deleting and creating proper icosphere
bpy.ops.object.delete(use_global=False)

# Create icosphere with 1 subdivision
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=1,
    radius=1.5,
    location=(0, 0, 3.5)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"

# Set smooth shading for better appearance
bpy.context.view_layer.objects.active = canopy
bpy.ops.object.shade_smooth()

bpy.context.view_layer.objects.active = trunk
bpy.ops.object.shade_smooth()

# Verify face count
trunk_faces = len(trunk.data.polygons)
canopy_faces = len(canopy.data.polygons)
total_faces = trunk_faces + canopy_faces

print(f"Trunk faces: {trunk_faces}")
print(f"Canopy faces: {canopy_faces}")
print(f"Total faces: {total_faces}")
