import bpy
import bmesh
from mathutils import Vector

# 1. Clear existing scene objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Create Wooden Post Mesh & Object
mesh_post = bpy.data.meshes.new("PostMesh")
obj_post = bpy.data.objects.new("FencePost", mesh_post)
bpy.context.collection.objects.link(obj_post)

bm = bmesh.new()
# Create a low-poly square wooden post with a slightly pointed/pyramid top
# Dimensions: 0.15m x 0.15m, height 1.8m
hw = 0.075
h = 1.8

verts = [
    bm.verts.new((-hw, -hw, 0.0)),
    bm.verts.new(( hw, -hw, 0.0)),
    bm.verts.new(( hw,  hw, 0.0)),
    bm.verts.new((-hw,  hw, 0.0)),
    bm.verts.new((-hw, -hw, h)),
    bm.verts.new(( hw, -hw, h)),
    bm.verts.new(( hw,  hw, h)),
    bm.verts.new((-hw,  hw, h)),
    bm.verts.new((0.0, 0.0, h + 0.1)) # Pyramid top center
]

# Base faces
bm.faces.new([verts[0], verts[1], verts[2], verts[3]]) # Bottom
bm.faces.new([verts[0], verts[4], verts[5], verts[1]]) # Side 1
bm.faces.new([verts[1], verts[5], verts[6], verts[2]]) # Side 2
bm.faces.new([verts[2], verts[6], verts[7], verts[3]]) # Side 3
bm.faces.new([verts[3], verts[7], verts[4], verts[0]]) # Side 4
# Top pyramid faces
bm.faces.new([verts[4], verts[7], verts[8]])
bm.faces.new([verts[7], verts[6], verts[8]])
bm.faces.new([verts[6], verts[5], verts[8]])
bm.faces.new([verts[5], verts[4], verts[8]])

bm.to_mesh(mesh_post)
bm.free()

# 3. Add Array Modifier to Post for 8 total posts
array_mod = obj_post.modifiers.new(name="PostArray", type='ARRAY')
array_mod.count = 8
array_mod.relative_offset_fit = 'FIXED'
array_mod.constant_offset_distance = (2.0, 0.0, 0.0) # 2 meters between posts

# 4. Create Wooden Rails Mesh & Object
mesh_rail = bpy.data.meshes.new("RailMesh")
obj_rail = bpy.data.objects.new("FenceRail", mesh_rail)
bpy.context.collection.objects.link(obj_rail)

bm_rail = bmesh.new()
# A horizontal rail spanning the 8 posts (total length = 7 intervals * 2.0m = 14.0m)
# Dimensions: thickness 0.08m, height 0.12m, length 14.0m
# We model one rail segment from x=0 to x=14
rx_start = 0.0
rx_end = 14.0
rhw = 0.04
rhh = 0.06
rz_center_1 = 0.6  # Lower rail
rz_center_2 = 1.4  # Upper rail

def create_beam(bm, x1, x2, z_center, hw, hh):
    v = [
        bm.verts.new((x1, -hw, z_center - hh)),
        bm.verts.new((x2, -hw, z_center - hh)),
        bm.verts.new((x2,  hw, z_center - hh)),
        bm.verts.new((x1,  hw, z_center - hh)),
        bm.verts.new((x1, -hw, z_center + hh)),
        bm.verts.new((x2, -hw, z_center + hh)),
        bm.verts.new((x2,  hw, z_center + hh)),
        bm.verts.new((x1,  hw, z_center + hh)),
    ]
    bm.faces.new([v[0], v[1], v[2], v[3]])
    bm.faces.new([v[4], v[7], v[6], v[5]])
    bm.faces.new([v[0], v[4], v[5], v[1]])
    bm.faces.new(
        [v[1], v[5], v[6], v[2]]
    )  # Fixed indent to match standard formatting style cleanly
    bm.faces.new([v[2], v[6], v[7], v[3]])
    bm.faces.new([v[3], v[7], v[4], v[0]])

create_beam(bm_rail, rx_start, rx_end, rz_center_1, rhw, rhh)
create_beam(bm_rail, rx_start, rx_end, rz_center_2, rhw, rhh)

bm_rail.to_mesh(mesh_rail)
bm_rail.free()

# 5. Create a simple Wood Material to give it a brownish procedural look
mat = bpy.data.materials.new(name="WoodMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.28, 0.16, 0.08, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.85

obj_post.data.materials.append(mat)
obj_rail.data.materials.append(mat)

# Ensure smooth shading is off for a low-poly look
for obj in [obj_post, obj_rail]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_flat()

# Final selection setup
bpy.ops.object.select_all(action='DESELECT')
obj_post.select_set(True)
bpy.context.view_layer.objects.active = obj_post
