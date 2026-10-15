import bpy
import bmesh
import mathutils
import math

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Helper to turn a bmesh into a mesh data-block
def mesh_from_bmesh(name, bm):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

# Rocket body: 8-sided cylinder, height 4, radius 1, from z=0 to z=4
bm = bmesh.new()
bmesh.ops.create_cone(
    bm,
    cap_ends=True,
    cap_tris=False,
    segments=8,
    diameter1=1,
    diameter2=1,
    depth=4,
)
bmesh.ops.translate(bm, vec=mathutils.Vector((0.0, 0.0, 2.0)), verts=bm.verts)
body_mesh = mesh_from_bmesh("BodyMesh", bm)
body_obj = bpy.data.objects.new("Body", body_mesh)
bpy.context.scene.collection.objects.link(body_obj)

# Nose cone: 8-sided pointed cone, height 2, base at z=4, tip at z=6
bm = bmesh.new()
bmesh.ops.create_cone(
    bm,
    cap_ends=False,
    cap_tris=False,
    segments=8,
    diameter1=1,
    diameter2=0,
    depth=2,
)
bmesh.ops.translate(bm, vec=mathutils.Vector((0.0, 0.0, 5.0)), verts=bm.verts)
nose_mesh = mesh_from_bmesh("NoseMesh", bm)
nose_obj = bpy.data.objects.new("Nose", nose_mesh)
bpy.context.scene.collection.objects.link(nose_obj)

# Fin base: cube shifted so it spans x = [0, 1] in local space
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
bmesh.ops.translate(bm, vec=mathutils.Vector((0.5, 0.0, 0.0)), verts=bm.verts)
fin_mesh = mesh_from_bmesh("FinMesh", bm)

# Three fins, rotated 120 degrees apart around the rocket's Z axis
for angle in (0, 120, 240):
    theta = math.radians(angle)
    fin_obj = bpy.data.objects.new("Fin", fin_mesh)
    bpy.context.scene.collection.objects.link(fin_obj)
    fin_obj.scale = (1.0, 0.15, 2.0)
    fin_obj.rotation_euler = (0.0, 0.0, theta)
    fin_obj.location = (math.cos(theta), math.sin(theta), 1.5)
