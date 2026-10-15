import bpy
import bmesh
import math
import mathutils

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the mug body: a cylinder, then remove its top face
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=1.5,
    location=(0.0, 0.0, 0.0),
    vertices=32
)
mug_obj = bpy.context.active_object
mug_obj.name = "Mug"

mesh = mug_obj.data
bm = bmesh.new()
bm.from_mesh(mesh)

# Top cap is at z = 0.75 for this cylinder
top_z = 0.75
top_faces = [f for f in bm.faces if all(v.co.z > top_z - 1e-5 for v in f.verts)]
if top_faces:
    bmesh.ops.delete(bm, geom=top_faces, context='FACES_ONLY')

# Make normals point outward (important for Solidify direction)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

# Add Solidify modifier to create the hollow cup wall
solidify_mod = mug_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify_mod.thickness = 0.1
solidify_mod.offset = -1.0  # extrude inward from the outward-facing normals

# Create a half-torus handle as a separate object
handle_major_radius = 0.6
handle_tube_radius = 0.1
handle_center_x = 0.95   # slightly embedded into the mug wall
handle_center_z = 0.0
major_segments = 16
tube_segments = 12

bm = bmesh.new()
verts = []

# Generate vertices for the half torus (theta from -pi/2 to pi/2)
for i in range(major_segments + 1):
    theta = -math.pi / 2.0 + math.pi * i / major_segments
    center = mathutils.Vector((
        handle_center_x + handle_major_radius * math.cos(theta),
        0.0,
        handle_center_z + handle_major_radius * math.sin(theta)
    ))
    radial = mathutils.Vector((math.cos(theta), 0.0, math.sin(theta)))
    y_axis = mathutils.Vector((0.0, 1.0, 0.0))

    for j in range(tube_segments):
        u = 2.0 * math.pi * j / tube_segments
        offset = handle_tube_radius * (math.cos(u) * radial + math.sin(u) * y_axis)
        verts.append(bm.verts.new(center + offset))

# Connect the vertices into quad faces
for i in range(major_segments):
    for j in range(tube_segments):
        v1 = i * tube_segments + j
        v2 = (i + 1) * tube_segments + j
        v3 = (i + 1) * tube_segments + (j + 1) % tube_segments
        v4 = i * tube_segments + (j + 1) % tube_segments
        bm.faces.new((verts[v1], verts[v4], verts[v3], verts[v2]))

# Make normals consistent (already outward, but keeps them clean)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

handle_mesh = bpy.data.meshes.new("HandleMesh")
bm.to_mesh(handle_mesh)
bm.free()

handle_obj = bpy.data.objects.new("Handle", handle_mesh)
bpy.context.collection.objects.link(handle_obj)
