import bpy
import bmesh
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Create Wooden Post Material ---
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs["Base Color"].default_value = (0.25, 0.15, 0.08, 1.0) # Rich wood brown
    principled.inputs["Roughness"].default_value = 0.8

# --- 1. Model a Single Post ---
# A low-poly post with a slanted top (to keep face count minimal)
bm = bmesh.new()
# Base box dimensions: width=0.15, depth=0.15, height=2.0
bmesh.ops.create_cube(bm, size=1.0)

# Scale and position to make it a post (bottom at Z=0, top at Z=2.0)
for v in bm.verts:
    v.co.x *= 0.15
    v.co.y *= 0.15
    v.co.z = (v.co.z + 0.5) * 2.0  # Z goes from 0 to 2.0

# Cut/slant the top by moving top vertices down on one side
for v in bm.verts:
    if v.co.z > 1.8:
        v.co.z -= v.co.x * 0.5  # Slight angle

mesh_post = bpy.data.meshes.new("PostMesh")
bm.to_mesh(mesh_post)
bm.free()

post_obj = bpy.data.objects.new("FencePost", mesh_post)
post_obj.data.materials.append(mat)
bpy.context.collection.objects.link(post_obj)

# --- 2. Add Array Modifier to Posts ---
# Total 8 posts, spaced along the X-axis
array_mod = post_obj.modifiers.new(name="PostArray", type='ARRAY')
array_mod.count = 8
array_mod.use_relative_offset = False
array_mod.use_constant_offset = True
array_mod.constant_offset_vector = (2.0, 0.0, 0.0) # 2 meters between posts

# --- 3. Model Horizontal Rails ---
# Create a single long rail mesh
bm_rail = bmesh.new()
bmesh.ops.create_cube(bm_rail, size=1.0)

# Scale into a long plank: length = 14.0 (covers 7 intervals of 2.0m), height = 0.1, depth = 0.05
for v in bm_rail.verts:
    v.co.x = (v.co.x + 0.5) * 14.0
    v.co.y = v.co.y * 0.05
    v.co.z = v.co.z * 0.1

mesh_rail = bpy.data.meshes.new("RailMesh")
bm_rail.to_mesh(mesh_rail)
bm_rail.free()

# Create Top Rail
top_rail = bpy.data.objects.new("TopRail", mesh_rail)
top_rail.data.materials.append(mat)
top_rail.location = (0.0, 0.0, 1.6) # Positioned near the top of the posts
bpy.context.collection.objects.link(top_rail)

# Create Bottom Rail
bottom_rail = bpy.data.objects.new("BottomRail", mesh_rail.copy())
bottom_rail.data.materials.append(mat)
bottom_rail.location = (0.0, 0.0, 0.6) # Positioned lower on the posts
bpy.context.collection.objects.link(bottom_rail)

# Select post object to keep scene clean
bpy.ops.object.select_all(action='DESELECT')
post_obj.select_set(True)
bpy.context.view_layer.objects.active = post_obj
