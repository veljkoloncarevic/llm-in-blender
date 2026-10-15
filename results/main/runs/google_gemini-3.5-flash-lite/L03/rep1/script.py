import bpy
import bmesh
from mathutils import Vector

# 1. Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 2. Create the Trunk (Cylinder with 8 sides)
# Radius 0.4, Depth 3.0, 8 vertices on cap
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.4,
    depth=3.0,
    vertices=8,
    location=(0, 0, 1.5)
)
trunk_obj = bpy.context.active_object
trunk_obj.name = "LowPolyTrunk"

# 3. Create the Canopy (Icosphere with 1 subdivision)
# Icosphere with 1 subdivision has 80 faces, keeps well under the 400 face limit.
bpy.ops.mesh.primitive_ico_sphere_add(
    radius=1.8,
    subdivisions=1,
    location=(0, 0, 3.8)
)
canopy_obj = bpy.context.active_object
canopy_obj.name = "LowPolyCanopy"

# 4. Stylize: Join them into a single low-poly tree object
bpy.ops.object.select_all(action='DESELECT')
trunk_obj.select_set(True)
canopy_obj.select_set(True)
bpy.context.view_layer.objects.active = trunk_obj
bpy.ops.object.join()

tree_obj = trunk_obj
tree_obj.name = "StylisedTree"

# 5. Apply low-poly flat shading
mesh = tree_obj.data
bm = bmesh.new()
bm.from_mesh(mesh)

for f in bm.faces:
    f.smooth = False

bm.to_mesh(mesh)
bm.free()
mesh.update()

# 6. Add simple materials for a stylized look
mat_trunk = bpy.data.materials.new(name="TrunkMaterial")
mat_trunk.use_nodes = True
mat_trunk.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.28, 0.18, 0.10, 1.0) # Brown

mat_canopy = bpy.data.materials.new(name="CanopyMaterial")
mat_canopy.use_nodes = True
mat_canopy.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.15, 0.45, 0.20, 1.0) # Green

# Assign materials to slots (Trunk faces vs Canopy faces)
# Since we joined them, we can assign materials by material index or per-face based on position.
# Let's assign materials cleanly:
tree_obj.data.materials.append(mat_trunk)
tree_obj.data.materials.append(mat_canopy)

# Assign canopy faces (Z > 2.5) to material slot 1, trunk to slot 0
for poly in tree_obj.data.polygons:
    # Check average position of polygon vertices to determine if it's trunk or canopy
    center = sum((tree_obj.matrix_world @ v.co for v in [tree_obj.data.vertices[vi] for vi in poly.vertices]), Vector()) / len(poly.vertices)
    if center.z > 2.5:
        poly.material_index = 1
    else:
        poly.material_index = 0
