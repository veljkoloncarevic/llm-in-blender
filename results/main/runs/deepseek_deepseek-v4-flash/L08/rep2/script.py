import bpy
import bmesh
import math

# Remove all existing objects from the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create the mug body ---
# Use bmesh to create a closed cylinder, then delete the top face.
depth = 1.5
segments = 32

mesh = bpy.data.meshes.new("MugBody")
bm = bmesh.new()

# Cylinder centered at origin, axis Z
bmesh.ops.create_cone(
    bm,
    segments=segments,
    diameter1=1.0,
    diameter2=1.0,
    depth=depth,
    cap_ends=True,
    cap_tris=False,
)

# Recenter cylinder so it spans z = -depth/2 .. depth/2
for v in bm.verts:
    v.co.z -= depth / 2.0

# Delete the top face (the n-gon with normal pointing +Z)
for f in list(bm.faces):
    if f.normal.z > 0.99:
        bm.faces.remove(f)

bm.to_mesh(mesh)
bm.free()

body_obj = bpy.data.objects.new("MugBody", mesh)
bpy.context.collection.objects.link(body_obj)

# Add Solidify modifier to make the wall hollow
solidify_mod = body_obj.modifiers.new("Solidify", 'SOLIDIFY')
solidify_mod.thickness = 0.1
solidify_mod.offset = 1.0  # extend outward from the original surface

# --- Create the handle ---
# A torus lying in the XZ plane, attached to the side of the cylinder.
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.5,
    minor_radius=0.1,
    major_segments=16,
    minor_segments=8,
    location=(1.0, 0.0, 0.0),
    rotation=(math.pi / 2, 0.0, 0.0)
)
handle_obj = bpy.context.active_object
handle_obj.name = "MugHandle"
