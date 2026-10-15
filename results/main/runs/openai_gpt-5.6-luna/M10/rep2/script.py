import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Chain parameters
link_count = 12
segments_around = 48
segments_tube = 16

major_radius = 1.45
minor_radius = 0.62
tube_radius = 0.16
link_spacing = 1.75

vertices = []
faces = []

def add_link(center_x, rotated):
    base_index = len(vertices)

    for i in range(segments_around):
        u = 2.0 * math.pi * i / segments_around
        cu = math.cos(u)
        su = math.sin(u)

        # Ellipse centerline and outward normal in its local plane
        ellipse_y = minor_radius * su
        ellipse_z = 0.0

        normal_y = cu / major_radius
        normal_z = su / minor_radius
        normal_length = math.sqrt(normal_y * normal_y + normal_z * normal_z)
        normal_y /= normal_length
        normal_z /= normal_length

        for j in range(segments_tube):
            v = 2.0 * math.pi * j / segments_tube
            cv = math.cos(v)
            sv = math.sin(v)

            local_x = major_radius * cu
            local_y = ellipse_y + tube_radius * cv * normal_y
            local_z = ellipse_z + tube_radius * (cv * normal_z + sv)

            # Rotate alternate links 90 degrees around the chain axis (X)
            if rotated:
                world_y = -local_z
                world_z = local_y
            else:
                world_y = local_y
                world_z = local_z

            vertices.append((
                center_x + local_x,
                world_y,
                world_z
            ))

    for i in range(segments_around):
        ni = (i + 1) % segments_around
        for j in range(segments_tube):
            nj = (j + 1) % segments_tube

            a = base_index + i * segments_tube + j
            b = base_index + ni * segments_tube + j
            c = base_index + ni * segments_tube + nj
            d = base_index + i * segments_tube + nj

            faces.append((a, b, c, d))

# Build alternating links along the X axis
for link_index in range(link_count):
    x = (link_index - (link_count - 1) * 0.5) * link_spacing
    add_link(x, link_index % 2 == 1)

# Create mesh
mesh = bpy.data.meshes.new("Interlocking_Chain_Mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

chain_object = bpy.data.objects.new("Interlocking_Chain", mesh)
bpy.context.collection.objects.link(chain_object)

# Smooth shading
for polygon in mesh.polygons:
    polygon.use_smooth = True

# Slightly weighted metallic material
material = bpy.data.materials.new("Chain_Metal")
material.diffuse_color = (0.18, 0.22, 0.28, 1.0)
material.metallic = 0.85
material.roughness = 0.24
chain_object.data.materials.append(material)

# Recalculate normals
bpy.context.view_layer.objects.active = chain_object
chain_object.select_set(True)
bpy.ops.object.shade_smooth()
