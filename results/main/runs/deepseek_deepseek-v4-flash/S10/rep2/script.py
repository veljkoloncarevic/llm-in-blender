import bpy
import bmesh

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create cube mesh data
mesh = bpy.data.meshes.new("Cube")
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=2)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()

# Create object and link to scene
obj = bpy.data.objects.new("Cube", mesh)
bpy.context.collection.objects.link(obj)

# Helper to create a material with a given base color
def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    principled = None
    for node in mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled = node
            break
    if principled is not None:
        principled.inputs['Base Color'].default_value = color
    mat.diffuse_color = color  # fallback / viewport color
    return mat

# Create three materials
red = create_material("Red", (1, 0, 0, 1))
green = create_material("Green", (0, 1, 0, 1))
blue = create_material("Blue", (0, 0, 1, 1))

# Add material slots
obj.data.materials.append(red)
obj.data.materials.append(green)
obj.data.materials.append(blue)

# Assign materials to faces based on face normals
for poly in obj.data.polygons:
    n = poly.normal
    if abs(n.x) > 0.9:
        poly.material_index = 0  # Red on X faces
    elif abs(n.y) > 0.9:
        poly.material_index = 1  # Green on Y faces
    elif abs(n.z) > 0.9:
        poly.material_index = 2  # Blue on Z faces
    else:
        poly.material_index = 0
