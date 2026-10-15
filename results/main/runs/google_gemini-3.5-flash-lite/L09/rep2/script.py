import bpy
import bmesh
from mathutils import Vector

# -------------------------------------------------------------------------
# Cleanup existing scene
# -------------------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove orphan data blocks
for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    for item in block:
        if item.users == 0:
            block.remove(item)

# -------------------------------------------------------------------------
# Materials Setup
# -------------------------------------------------------------------------
wood_mat = bpy.data.materials.new(name="Wood_Material")
wood_mat.use_nodes = True
bsdf = wood_mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    # Warm brownish wood color
    bsdf.inputs['Base Color'].default_value = (0.28, 0.16, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75

# -------------------------------------------------------------------------
# 1. Base Post Modeling (Low Poly, < 100 faces)
# -------------------------------------------------------------------------
bm = bmesh.new()
# Create a rectangular prism for the post: width=0.15, depth=0.15, height=2.0
bmesh.ops.create_cube(bm, size=1.0)

# Scale and position so pivot is at the bottom-center of the post
# Size is 1m, so scale X/Y to 0.15, Z to 2.0, then translate Z by +1.0 (half height)
matrix_transform = Vector((0.15, 0.15, 2.0))
matrix_translate = Vector((0, 0, 1.0))

for v in bm.verts:
    v.co.x *= matrix_transform.x
    v.co.y *= matrix_transform.y
    v.co.z *= matrix_transform.z
    v.co.z += matrix_translate.z

# Add a simple pyramid cap to the top of the post (Z = 2.0)
top_verts = [v for v in bm.verts if v.co.z > 1.99]
if top_verts:
    # Calculate center of top face
    center = sum((v.co for v in top_verts), Vector()) / len(top_verts)
    apex = center + Vector((0, 0, 0.12))
    apex_vert = bm.verts.new(apex)
    
    # Reconnect top faces to form a pointed cap
    # Since it's a cube top, we can make 4 triangles from the sides up to the apex
    # For simplicity in low-poly, just extrude/bevel the top face up
    pass

# Alternatively, let's keep it clean: a simple box post with a bevel-like top or just pure low-poly box.
# Let's add a slight taper at the very top for a classic fence post look.
for v in bm.verts:
    if v.co.z > 1.99:
        # Inward push on X and Y based on original
        v.co.x *= 0.6
        v.co.y *= 0.6
        v.co.z = 2.15  # peak height

mesh_post = bpy.data.meshes.new("FencePost_Mesh")
bm.to_mesh(mesh_post)
bm.free()

obj_post = bpy.data.objects.new("FencePost", mesh_post)
bpy.context.collection.objects.link(obj_post)
obj_post.data.materials.append(wood_mat)

# -------------------------------------------------------------------------
# 2. Array Modifier for Posts (8 posts total)
# -------------------------------------------------------------------------
array_mod = obj_post.modifiers.new(name="PostArray", type='ARRAY')
array_mod.count = 8
array_mod.relative_offset_fix = [0.0, 0.0, 0.0]
array_mod.use_relative_offset = False
array_mod.use_constant_offset = True
# Space posts 1.5 meters apart along X axis
array_mod.constant_offset_vector = (1.5, 0.0, 0.0)

# -------------------------------------------------------------------------
# 3. Horizontal Rails Modeling
# -------------------------------------------------------------------------
# We need two horizontal rails spanning across the 8 posts.
# Total length = (8 - 1) * 1.5 = 10.5 meters span.
# Let's build a single rail object that spans the entire length, 
# positioned appropriately in Z.

bm_rail = bmesh.new()
bmesh.ops.create_cube(bm_rail, size=1.0)

# Dimensions: length = 10.5 (X), width = 0.08 (Y), height = 0.12 (Z)
# Pivot at start (X=0), so shift X by half-length (5.25)
rail_length = 10.5
for v in bm_rail.verts:
    v.co.x *= rail_length
    v.co.y *= 0.08
    v.co.z *= 0.12
    v.co.x += rail_length * 0.5  # shift so start is at X=0

mesh_rail = bpy.data.meshes.new("FenceRail_Mesh")
bm_rail.to_mesh(mesh_rail)
bm_rail.free()

# Create Top Rail
obj_top_rail = bpy.data.objects.new("FenceRail_Top", mesh_rail)
bpy.context.collection.objects.link(obj_top_rail)
obj_top_rail.data.materials.append(wood_mat)
obj_top_rail.location = (0.0, 0.0, 1.7)  haus_z = 1.7

# Create Bottom Rail
obj_bot_rail = bpy.data.objects.new("FenceRail_Bottom", mesh_rail)
bpy.context.collection.objects.link(obj_bot_rail)
obj_bot_rail.data.materials.append(wood_mat)
obj_bot_rail.location = (0.0, 0.0, 0.6)

# -------------------------------------------------------------------------
# Final Scene Setup
# -------------------------------------------------------------------------
# Ensure objects are selected properly if needed, face counts remain well under 1,000.
# Post: ~10 faces * 8 = 80 faces.
# Rails: ~6 faces each * 2 = 12 faces.
# Total geometry is extremely optimized and clean.
bpy.context.view_layer.update()
