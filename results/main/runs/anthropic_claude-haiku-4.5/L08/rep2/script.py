import bpy
import bmesh
from mathutils import Matrix
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the mug body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.8,
    depth=2.0,
    vertices=16,
    location=(0, 0, 1)
)
mug_body = bpy.context.active_object
mug_body.name = "MugBody"

# Enter edit mode and delete the top face to make it open
bpy.context.view_layer.objects.active = mug_body
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.delete(type='ONLY_FACE')
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier to make it hollow
solidify = mug_body.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.1
solidify.offset = 0

# Create the handle (half torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.1,
    location=(0.8, 0, 1),
    rotation=(math.pi/2, 0, 0)
)
handle = bpy.context.active_object
handle.name = "Handle"

# Delete half of the torus to make a handle shape
bpy.context.view_layer.objects.active = handle
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Select vertices on one side and delete them
mesh = handle.data
for vertex in mesh.vertices:
    if vertex.co.y > 0.05:
        vertex.select = True

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.delete(type='VERT')
bpy.ops.object.mode_set(mode='OBJECT')

# Join the objects
bpy.context.view_layer.objects.active = mug_body
mug_body.select_set(True)
handle.select_set(True)
bpy.ops.object.join()

# Final object is now the mug with handle
final_mug = bpy.context.active_object
final_mug.name = "CoffeeMug"

# Ensure we're in object mode
bpy.ops.object.mode_set(mode='OBJECT')
