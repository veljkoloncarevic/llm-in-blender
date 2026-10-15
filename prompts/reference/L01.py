# Hand-written reference solution (used by --smoke to test the pipeline without API calls)
import bpy

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
top = bpy.context.active_object
top.name = "Tabletop"
top.scale = (1.2, 0.7, 0.05)
bevel = top.modifiers.new("Bevel", "BEVEL")
bevel.width = 0.01
bevel.segments = 2

for x in (-0.55, 0.55):
    for y in (-0.3, 0.3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, 0.36))
        leg = bpy.context.active_object
        leg.name = "Leg"
        leg.scale = (0.06, 0.06, 0.72)
