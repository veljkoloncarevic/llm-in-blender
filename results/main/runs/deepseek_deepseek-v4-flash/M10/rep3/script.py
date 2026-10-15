import bpy
import bmesh
import math
from mathutils import Vector, Euler


def clear_scene():
    """Remove all existing objects from the scene."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def create_link_mesh(seg_major, seg_minor, major_radius, minor_radius, oval_scale):
    """
    Create an oval (elliptical) torus-shaped link in the XY plane.
    The major axis of the oval is along X.
    Returns a bmesh.
    """
    A = major_radius * oval_scale
    B = major_radius
    r = minor_radius

    bm = bmesh.new()
    verts = []

    for i in range(seg_major):
        theta = 2 * math.pi * i / seg_major

        # Point on the central ellipse
        cx = A * math.cos(theta)
        cy = B * math.sin(theta)

        # Tangent vector
        tx = -A * math.sin(theta)
        ty = B * math.cos(theta)

        # Normal vector in the plane (perpendicular to tangent)
        nx = B * math.cos(theta)
        ny = A * math.sin(theta)
        n_len = math.hypot(nx, ny)
        nx /= n_len
        ny /= n_len

        row = []
        for j in range(seg_minor):
            phi = 2 * math.pi * j / seg_minor

            # Tube point: C + r * (cos(phi)*N + sin(phi)*Z)
            px = cx + r * (math.cos(phi) * nx)
            py = cy + r * (math.cos(phi) * ny)
            pz = r * math.sin(phi)

            row.append(bm.verts.new((px, py, pz)))
        verts.append(row)

    # Create quad faces
    for i in range(seg_major):
        i2 = (i + 1) % seg_major
        for j in range(seg_minor):
            j2 = (j + 1) % seg_minor
            v1 = verts[i][j]
            v2 = verts[i2][j]
            v3 = verts[i2][j2]
            v4 = verts[i][j2]
            try:
                bm.faces.new((v1, v2, v3, v4))
            except ValueError:
                pass

    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm


def place_link(bm, location, rot_x_angle):
    """Transform a link bmesh: rotate around X then translate."""
    rot = Euler((rot_x_angle, 0, 0), 'XYZ').to_matrix()
    trans = Vector(location)
    for v in bm.verts:
        v.co = rot @ v.co + trans


def add_link_object(name, bm):
    """Convert bmesh to mesh and add as object to current collection."""
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def main():
    clear_scene()

    num_links = 12
    seg_major = 48
    seg_minor = 12
    major_radius = 1.0
    minor_radius = 0.12
    oval_scale = 1.5
    spacing = 1.7

    for i in range(num_links):
        bm = create_link_mesh(
            seg_major,
            seg_minor,
            major_radius,
            minor_radius,
            oval_scale,
        )
        loc = (i * spacing, 0, 0)
        angle = i * math.pi / 2  # 90 degree rotation per step
        place_link(bm, loc, angle)
        add_link_object(f"Oval_Link_{i}", bm)


if __name__ == "__main__":
    main()
