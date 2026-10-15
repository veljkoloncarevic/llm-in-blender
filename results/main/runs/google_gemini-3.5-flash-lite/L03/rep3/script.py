import bpy
import bmesh

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create trunk (cylinder with 8 vertices)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.4,
    depth=2.0,
    location=(0, 0, 1.0)
)
trunk = bpy.context.active_object
trunk.name = "StylizedTrunk"

# Create canopy (icosphere with 1 subdivision for low-poly look, total faces = 80)
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=1,
    radius=1.5,
    location=(0, 0, 3.2)
)
canopy = bpy.context.active_object
canopy.name = "StylizedCanopy"

# Create a simple low-poly material for the trunk (Brown)
mat_trunk = bpy.data.materials.new(name="TrunkMaterial")
mat_trunk.use_nodes = False
mat_trunk.diffuse_color = (0.25, 0.15, 0.08, 1.0)
trunk.data.materials.append(mat_trunk)

# Create a simple low-poly material for the canopy (Stylized Green)
mat_canopy = bpy.data.materials.new(name="CanopyMaterial")
mat_canopy.use_nodes = False
mat_canopy.diffuse_color = (0.15, 0.55, 0.2, 1.0)
canopy.data.materials.append(mat_canopy)

# Apply flat shading to both objects to reinforce the low-poly aesthetic
for obj in [trunk, canopy]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_flat()

# Select both objects and join them into a single low-poly tree mesh
bpy.ops.object.select_all(action='DESELECT')
trunk.select_set(True)
canopy.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.object.join()

tree = bpy.context.active_object
tree.name = "StylizedTree"

# Ensure origin is at the base of the trunk
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
# Move origin back to world Z=0 relative to the mesh base
# (Bounding box center is roughly middle, let's snap origin to bottom using bmesh)
bm = bmesh.new()
bm.from_mesh(tree.data)
min_z = min(v.co.z for v in bm.verts)
for v in bm.verts:
    v.co.z -= min_z
bm.to_mesh(tree.data)
bm.free()
tree.location.z = 0
