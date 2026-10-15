import bpy

# Remove all existing objects
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create materials
trunk_material = bpy.data.materials.new("Trunk Material")
trunk_material.diffuse_color = (0.24, 0.09, 0.025, 1.0)
trunk_material.roughness = 1.0

canopy_material = bpy.data.materials.new("Canopy Material")
canopy_material.diffuse_color = (0.08, 0.38, 0.10, 1.0)
canopy_material.roughness = 1.0

# Create the 8-sided cylindrical trunk
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.48,
    depth=3.0,
    end_fill_type='NGON',
    location=(0.0, 0.0, 1.5)
)
trunk = bpy.context.object
trunk.name = "Low Poly Trunk"
trunk.data.materials.append(trunk_material)

for polygon in trunk.data.polygons:
    polygon.use_smooth = False

# Create the low-poly icosphere canopy
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=1.8,
    location=(0.0, 0.0, 3.55)
)
canopy = bpy.context.object
canopy.name = "Low Poly Canopy"
canopy.scale = (1.15, 1.05, 1.0)
canopy.data.materials.append(canopy_material)

for polygon in canopy.data.polygons:
    polygon.use_smooth = False
