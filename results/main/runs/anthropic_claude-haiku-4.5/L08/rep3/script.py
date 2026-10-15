import bpy
import bmesh
from mathutils import Matrix, Vector
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the mug body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.8,
    depth=2.0,
    vertices=16,  # Keep low for face count
    location=(0, 0, 1)
)
mug_body = bpy.context.active_object
mug_body.name = "MugBody"

# Remove the top face to make it open
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mug_body.data)

# Select top face
for face in bm.faces:
    center = face.calc_center_median()
    if center.z > 1.5:  # Top face
        face.select = True
    else:
        face.select = False

# Delete top face
bpy.ops.mesh.delete(type='FACE')
bmesh.update_edit_mesh(mug_body.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier to make it hollow
solidify = mug_body.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify.thickness = 0.1
solidify.offset = 0

# Create the handle (torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.15,
    major_segments=12,
    minor_segments=6,
    location=(1.2, 0, 1)
)
handle = bpy.context.active_object
handle.name = "Handle"

# Rotate handle to be vertical and positioned correctly
handle.rotation_euler = (math.pi / 2, 0, 0)
handle.location = (1.1, 0, 1)

# Delete half of the handle to make it a semi-circle
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(handle.data)

# Select vertices on one side to delete
for vertex in bm.verts:
    if vertex.co.y > 0.05:
        vertex.select = True
    else:
        vertex.select = False

bpy.ops.mesh.delete(type='VERT')
bmesh.update_edit_mesh(handle.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Join the objects
bpy.context.view_layer.objects.active = mug_body
mug_body.select_set(True)
handle.select_set(True)
bpy.ops.object.join()

# Ensure we're in object mode
bpy.ops.object.mode_set(mode='OBJECT')
