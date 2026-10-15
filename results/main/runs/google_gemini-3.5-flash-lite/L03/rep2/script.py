import bpy
import bmesh
from mathutils import Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create trunk (cylinder with 8 vertices)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.4,
    depth=2.5,
    location=(0, 0, 1.25)
)
trunk = bpy.context.active_object
trunk.name = "LowPolyTrunk"

# Create canopy (icosphere with 2 subdivisions)
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.8,
    location=(0, 0, 3.2)
)
canopy = bpy.context.active_object
canopy.name = "LowPolyCanopy"

# Stylize the canopy: slightly deform it using bmesh for a faceted, organic look
mesh = canopy.data
bm = bmesh.from_edit_mesh(mesh)

# Rotate canopy slightly for natural variation
bmesh.ops.rotate(
    bm,
    cent=(0, 0, 3.2),
    matrix=Matrix.Rotation(0.5, 3, 'Z'),
    verts=bm.verts
)

bmesh.update_edit_mesh(mesh)

# Create and assign materials
mat_trunk = bpy.data.materials.new(name="TrunkMaterial")
mat_trunk.use_nodes = False
mat_trunk.diffuse_color = (0.25, 0.15, 0.08, 1.0) # Warm brown
trunk.data.materials.append(mat_trunk)

mat_canopy = bpy.data.materials.new(name="CanopyMaterial")
mat_canopy.use_nodes = False
mat_canopy.diffuse_color = (0.12, 0.45, 0.18, 1.0) # Stylized green
canopy.data.materials.append(mat_canopy)

# Join objects into a single stylized tree mesh to keep it clean and unified
bpy.ops.object.select_all(action='DESELECT')
trunk.select_set(True)
canopy.select_set(True)
bpy.context.view_layer.objects.active = trunk
bpy.ops.object.join()

tree = trunk
tree.name = "StylizedLowPolyTree"

# Set shading to flat for the low-poly aesthetic
bpy.ops.object.shade_flat()
