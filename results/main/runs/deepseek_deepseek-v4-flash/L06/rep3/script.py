import bpy
import bmesh
from mathutils import Vector, Matrix

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the cube (die body)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
die = bpy.context.object
die.name = "Die"

# Store face information from the original cube before adding the bevel
mesh = die.data
face_data = []
for f in mesh.polygons:
    n = f.normal.copy()
    center = f.center.copy()

    # Map normals to pip values (opposite faces sum to 7)
    if abs(n.x) > 0.5:
        value = 1 if n.x > 0 else 6
    elif abs(n.y) > 0.5:
        value = 2 if n.y > 0 else 5
    elif abs(n.z) > 0.5:
        value = 3 if n.z > 0 else 4
    else:
        continue

    # Build two tangent vectors inside the face plane
    axis = Vector((1, 0, 0))
    if abs(n.x) >= 0.999:
        axis = Vector((0, 1, 0))
    t1 = n.cross(axis)
    if t1.length_squared < 1e-12:
        t1 = n.cross(Vector((0, 1, 0)))
    t1.normalize()
    t2 = n.cross(t1).normalize()

    face_data.append((center, n, t1, t2, value))

# Add and keep the Bevel modifier with 3 segments
bevel = die.modifiers.new(name="Bevel", type='BEVEL')
bevel.segments = 3
bevel.width = 0.15
bevel.limit_method = 'NONE'

# Pip patterns for faces 1..6 (grid coordinates -1, 0, 1)
patterns = {
    1: ((0, 0),),
    2: ((-1, -1), (1, 1)),
    3: ((-1, -1), (0, 0), (1, 1)),
    4: ((-1, -1), (1, 1), (1, -1), (-1, 1)),
    5: ((-1, -1), (1, 1), (1, -1), (-1, 1), (0, 0)),
    6: ((-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)),
}

# Build all pips as one mesh
pip_mesh = bpy.data.meshes.new("Pips")
bm = bmesh.new()

spacing = 0.6
pip_radius = 0.08
pip_depth = 0.03
pip_segments = 8
base_inset = 0.002  # slightly embed bases to avoid z-fighting

for center, n, t1, t2, value in face_data:
    for du, dv in patterns[value]:
        loc = center + t1 * (du * spacing) + t2 * (dv * spacing) - n * base_inset
        q = n.normalized().to_track_quat('Z', 'Y')
        mat = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=pip_segments,
            radius1=pip_radius,
            radius2=pip_radius,
            depth=pip_depth,
            matrix=mat,
        )

bm.to_mesh(pip_mesh)
bm.free()

# Link the pips object to the scene
pip_obj = bpy.data.objects.new("Pips", pip_mesh)
bpy.context.collection.objects.link(pip_obj)
