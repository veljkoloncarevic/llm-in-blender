import bpy

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create trunk material
trunk_material = bpy.data.materials.new("Trunk Material")
trunk_material.diffuse_color = (0.24, 0.09, 0.035, 1.0)
trunk_material.roughness = 1.0

# Create canopy material
canopy_material = bpy.data.materials.new("Canopy Material")
canopy_material.diffuse_color = (0.08, 0.38, 0.10, 1.0)
canopy_material.roughness = 1.0

# Low-poly eight-sided cylindrical trunk
bpy.ops.mesh.primitive_cylinder_add(
    vertices=8,
    radius=0.6,
    depth=3.0,
    end_fill_type='NGON',
    location=(0.0, 0.0, 1.5)
)
trunk = bpy.context.object
trunk.name = "Eight-Sided Trunk"
trunk.data.materials.append(trunk_material)

for polygon in trunk.data.polygons:
    polygon.use_smooth = False

# Low-poly icosphere canopy, subdivision level 2
bpy.ops.mesh.primitive_ico_sphere_add(
    subdivisions=2,
    radius=2.0,
    location=(0.0, 0.0, 4.0)
)
canopy = bpy.context.object
canopy.name = "Low-Poly Canopy"
canopy.data.materials.append(canopy_material)

for polygon in canopy.data.polygons:
    polygon.use_smooth = False
