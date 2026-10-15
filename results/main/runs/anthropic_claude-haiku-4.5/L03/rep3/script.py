import bpy
import bmesh
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create trunk (8-sided cylinder)
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.3,
    depth=2.0,
    location=(0, 0, 1.0)
)
trunk = bpy.context.active_object
trunk.name = "Trunk"

# Create canopy (icosphere with minimal subdivisions)
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=1.5,
    location=(0, 0, 3.0)
)
canopy = bpy.context.active_object
canopy.name = "Canopy"

# Convert sphere to icosphere by using bmesh
bpy.context.view_layer.objects.active = canopy
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(canopy.data)

# Delete all faces and start fresh with icosphere
bm.clear()

# Create icosphere manually with 1 subdivision (minimal)
phi = (1.0 + 5.0**0.5) / 2.0
vertices_coords = [
    (-1, phi, 0),
    (1, phi, 0),
    (-1, -phi, 0),
    (1, -phi, 0),
    (0, -1, phi),
    (0, 1, phi),
    (0, -1, -phi),
    (0, 1, -phi),
    (phi, 0, -1),
    (phi, 0, 1),
    (-phi, 0, -1),
    (-phi, 0, 1),
]

# Normalize vertices
for i, coord in enumerate(vertices_coords):
    length = (coord[0]**2 + coord[1]**2 + coord[2]**2)**0.5
    vertices_coords[i] = (coord[0]/length, coord[1]/length, coord[2]/length)

# Create vertices
verts = [bm.verts.new(coord) for coord in vertices_coords]
bm.verts.ensure_lookup_table()

# Create icosphere faces (20 triangles)
faces_indices = [
    (0, 11, 5),
    (0, 5, 1),
    (0, 1, 7),
    (0, 7, 10),
    (0, 10, 11),
    (1, 5, 9),
    (5, 11, 4),
    (11, 10, 2),
    (10, 7, 6),
    (7, 1, 8),
    (3, 9, 4),
    (3, 4, 2),
    (3, 2, 6),
    (3, 6, 8),
    (3, 8, 9),
    (4, 9, 5),
    (2, 4, 11),
    (6, 2, 10),
    (8, 6, 7),
    (9, 8, 1),
]

for face_indices in faces_indices:
    bm.faces.new([verts[i] for i in face_indices])

bmesh.update_edit_mesh(canopy.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Scale canopy to appropriate size
canopy.scale = (1.5, 1.5, 1.5)

# Apply a simple material to differentiate trunk and canopy
trunk_mat = bpy.data.materials.new(name="TrunkMaterial")
trunk_mat.use_nodes = True
trunk_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.4, 0.25, 0.1, 1.0)
trunk.data.materials.append(trunk_mat)

canopy_mat = bpy.data.materials.new(name="CanopyMaterial")
canopy_mat.use_nodes = True
canopy_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.6, 0.1, 1.0)
canopy.data.materials.append(canopy_mat)

# Verify face count
trunk_faces = len(trunk.data.polygons)
canopy_faces = len(canopy.data.polygons)
total_faces = trunk_faces + canopy_faces

print(f"Trunk faces: {trunk_faces}")
print(f"Canopy faces: {canopy_faces}")
print(f"Total faces: {total_faces}")
