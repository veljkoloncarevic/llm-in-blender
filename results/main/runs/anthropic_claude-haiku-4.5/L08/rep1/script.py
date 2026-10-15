import bpy
import bmesh
from mathutils import Matrix, Vector
import math

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the mug body as a cylinder
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.8,
    depth=2.0,
    vertices=16,
    location=(0, 0, 1)
)
mug_body = bpy.context.active_object
mug_body.name = "MugBody"

# Enter edit mode to make it hollow by deleting top face
bpy.context.view_layer.objects.active = mug_body
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles()
bpy.ops.object.mode_set(mode='OBJECT')

# Select top face and delete it
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Get the mesh and select top vertices
mesh = mug_body.data
for v in mesh.vertices:
    if v.co.z > 1.5:
        v.select = True

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='FACE')
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier to make walls
solidify = mug_body.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.1
solidify.offset = 0

# Create the handle as a torus
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.6,
    minor_radius=0.15,
    location=(1.0, 0, 1.2)
)
handle = bpy.context.active_object
handle.name = "Handle"

# Rotate handle to be vertical and positioned correctly
handle.rotation_euler = (math.pi / 2, 0, 0)
handle.location = (1.1, 0, 1.0)

# Scale down the torus segments for fewer faces
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Join handle to body
bpy.context.view_layer.objects.active = mug_body
handle.select_set(True)
bpy.ops.object.join()

# Final cleanup
bpy.context.view_layer.objects.active = mug_body
bpy.ops.object.shade_smooth()

print(f"Mug created with {len(mug_body.data.vertices)} vertices and {len(mug_body.data.polygons)} faces")
