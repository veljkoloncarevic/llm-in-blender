import bpy
import bmesh
import math
from mathutils import Matrix, Vector

# Remove existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a single mesh for the honeycomb panel
bm = bmesh.new()

# Parameters
rows = 10
cols = 10
cell_radius = 1.0      # layout spacing radius (gaps are created by using a smaller hex)
hex_radius = 0.8       # actual hexagon circumradius -> small gaps
height = 0.5           # prism extrusion height

spacing_x = math.sqrt(3) * cell_radius
spacing_y = 1.5 * cell_radius
row_offset = spacing_x / 2.0

for r in range(rows):
    y = r * spacing_y
    x_off = row_offset if r % 2 == 1 else 0.0
    for c in range(cols):
        center = Vector((c * spacing_x + x_off, y, 0.0))
        mat = Matrix.Translation(center) @ Matrix.Rotation(math.radians(30), 4, 'Z')

        # Create one hexagonal cap (pointy-top orientation)
        res = bmesh.ops.create_circle(
            bm,
            cap_ends=True,
            radius=hex_radius,
            vertices=6,
            matrix=mat
        )
        face = res['faces'][0]

        # Extrude the hexagon into a prism
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        bmesh.ops.translate(bm, verts=extruded['verts'], vec=Vector((0.0, 0.0, height)))

# Ensure outward-facing normals
bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))

# Center the panel in XY
verts = list(bm.verts)
xs = [v.co.x for v in verts]
ys = [v.co.y for v in verts]
center = Vector(((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, 0.0))
bmesh.ops.translate(bm, verts=verts, vec=-center)

# Write the mesh into a Blender object
mesh = bpy.data.meshes.new("HoneycombPanel")
bm.to_mesh(mesh)
bm.free()

obj = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(obj)
obj.location = (0.0, 0.0, 0.0)
