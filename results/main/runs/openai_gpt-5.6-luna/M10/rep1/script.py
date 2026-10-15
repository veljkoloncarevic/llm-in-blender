import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Link and chain parameters
link_count = 12
major_radius = 1.15
minor_radius = 0.52
tube_radius = 0.14
spacing = 1.45

# Mesh resolution
major_segments = 48
tube_segments = 12

# Material
material = bpy.data.materials.new("Chain Metal")
material.diffuse_color = (0.12, 0.16, 0.22, 1.0)
material.metallic = 0.8
material.roughness = 0.24

for link_index in range(link_count):
    center_x = (link_index - (link_count - 1) * 0.5) * spacing
    rotated = (link_index % 2) == 1

    vertices = []
    faces = []

    for i in range(major_segments):
        t = 2.0 * math.pi * i / major_segments

        # Elliptical centerline in the local XY plane
        local_center = Vector((
            major_radius * math.cos(t),
            minor_radius * math.sin(t),
            0.0
        ))

        # Tangent and in-plane normal of the ellipse
        tangent = Vector((
            -major_radius * math.sin(t),
            minor_radius * math.cos(t),
            0.0
        )).normalized()

        in_plane_normal = Vector((
            -tangent.y,
            tangent.x,
            0.0
        )).normalized()

        binormal = Vector((0.0, 0.0, 1.0))

        for j in range(tube_segments):
            q = 2.0 * math.pi * j / tube_segments
            ring_offset = tube_radius * (
                math.cos(q) * in_plane_normal +
                math.sin(q) * binormal
            )

            point = local_center + ring_offset

            # Alternate link planes by 90 degrees around the chain axis (X)
            if rotated:
                point = Vector((point.x, -point.z, point.y))

            point.x += center_x
            vertices.append(tuple(point))

    for i in range(major_segments):
        next_i = (i + 1) % major_segments

        for j in range(tube_segments):
            next_j = (j + 1) % tube_segments

            a = i * tube_segments + j
            b = next_i * tube_segments + j
            c = next_i * tube_segments + next_j
            d = i * tube_segments + next_j

            faces.append((a, b, c, d))

    mesh = bpy.data.meshes.new(f"Oval_Link_{link_index + 1:02d}")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(f"Oval_Link_{link_index + 1:02d}", mesh)
    bpy.context.collection.objects.link(obj)

    obj.data.materials.append(material)

    for polygon in mesh.polygons:
        polygon.use_smooth = True

    # Weighted normals are not required; the dense quad topology provides
    # smooth shading while preserving the oval link silhouette.
