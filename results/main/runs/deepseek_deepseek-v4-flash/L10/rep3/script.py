import bpy
import bmesh

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Walls: a cube scaled to 4x4x3, centered at z=1.5
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.5))
walls = bpy.context.active_object
walls.name = "Walls"
walls.scale = (2, 2, 1.5)

# Roof: four-sided pyramid made with bmesh
bm = bmesh.new()
b0 = bm.verts.new((2.3, 2.3, 3.0))
b1 = bm.verts.new((-2.3, 2.3, 3.0))
b2 = bm.verts.new((-2.3, -2.3, 3.0))
b3 = bm.verts.new((2.3, -2.3, 3.0))
top = bm.verts.new((0.0, 0.0, 4.5))
bm.faces.new((b0, b1, top))
bm.faces.new((b1, b2, top))
bm.faces.new((b2, b3, top))
bm.faces.new((b3, b0, top))

roof_mesh = bpy.data.meshes.new("RoofMesh")
bm.to_mesh(roof_mesh)
bm.free()
roof = bpy.data.objects.new("Roof", roof_mesh)
bpy.context.scene.collection.objects.link(roof)

# Door: flat rectangle on the front wall
bm = bmesh.new()
d0 = bm.verts.new((-0.45, -1.99, 0.0))
d1 = bm.verts.new((0.45, -1.99, 0.0))
d2 = bm.verts.new((0.45, -1.99, 2.0))
d3 = bm.verts.new((-0.45, -1.99, 2.0))
bm.faces.new((d0, d1, d2, d3))

door_mesh = bpy.data.meshes.new("DoorMesh")
bm.to_mesh(door_mesh)
bm.free()
door = bpy.data.objects.new("Door", door_mesh)
bpy.context.scene.collection.objects.link(door)

# Window: flat rectangle on the right side of the front wall
# A Mirror modifier will create the symmetric left-side window.
bm = bmesh.new()
w0 = bm.verts.new((0.8, -1.99, 1.1))
w1 = bm.verts.new((1.6, -1.99, 1.1))
w2 = bm.verts.new((1.6, -1.99, 1.9))
w3 = bm.verts.new((0.8, -1.99, 1.9))
bm.faces.new((w0, w1, w2, w3))

window_mesh = bpy.data.meshes.new("WindowMesh")
bm.to_mesh(window_mesh)
bm.free()
window = bpy.data.objects.new("Window", window_mesh)
bpy.context.scene.collection.objects.link(window)

# Add Mirror modifier to the window for symmetric placement
bpy.ops.object.select_all(action='DESELECT')
window.select_set(True)
bpy.context.view_layer.objects.active = window
bpy.ops.object.modifier_add(type='MIRROR')
mod = window.modifiers["Mirror"]
mod.use_axis[0] = True
mod.use_axis[1] = False
mod.use_axis[2] = False
