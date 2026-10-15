import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Chain parameters
link_count = 12
major_radius = 1.35
minor_radius = 0.62
tube_radius = 0.16
link_spacing = 1.75

major_segments = 64
tube_segments = 16

def create_oval_link(name, center_x, orientation):
    """
    Creates an oval tubular link.
    orientation 0: oval lies in the XY plane, normal along Z
    orientation 1: oval lies in the XZ plane, normal along Y
    """
    vertices = []
    faces = []

    if orientation == 0:
        transverse = Vector((0.0, 1.0, 0.0))
        normal = Vector((0.0, 0.0, 1.0))
    else:
        transverse = Vector((0.0, 0.0, 1.0))
        normal = Vector((0.0, 1.0, 0.0))

    axis = Vector((1.0, 0.0, 0.0))
    center = Vector((center_x, 0.0, 0.0))

    for i in range(major_segments):
        u = 2.0 * math.pi * i / major_segments
        cu = math.cos(u)
        su = math.sin(u)

        # Centerline of the oval
        centerline = center + axis * (major_radius * cu) + transverse * (minor_radius * su)

        # Approximate outward-facing radial direction in the oval's plane
        radial = (axis * su + transverse * cu).normalized()

        for j in range(tube_segments):
            v = 2.0 * math.pi * j / tube_segments
            cv = math.cos(v)
            sv = math.sin(v)

            vertex = (
                centerline
                + radial * (tube_radius * cv)
                + normal * (tube_radius * sv)
            )
            vertices.append(tuple(vertex))

    for i in range(major_segments):
        ni = (i + 1) % major_segments
        for j in range(tube_segments):
            nj = (j + 1) % tube_segments

            a = i * tube_segments + j
            b = ni * tube_segments + j
            c = ni * tube_segments + nj
            d = i * tube_segments + nj
            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    for polygon in mesh.polygons:
        polygon.use_smooth = True

    return obj

# Build alternating links, each rotated 90 degrees about the chain axis
for i in range(link_count):
    orientation = i % 2
    create_oval_link(
        name=f"Oval_Link_{i + 1:02d}",
        center_x=(i - (link_count - 1) / 2.0) * link_spacing,
        orientation=orientation
    )
