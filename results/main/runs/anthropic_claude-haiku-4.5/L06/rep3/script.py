import bpy
import bmesh
from mathutils import Vector
from math import pi

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the main cube for the die
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
die = bpy.context.active_object
die.name = "Die"

# Add Bevel modifier with 3 segments
bevel = die.modifiers.new(name="Bevel", type='BEVEL')
bevel.width = 0.15
bevel.segments = 3
bevel.affect = 'EDGES'

# Define pip positions for each face (center and count)
# Face normals: +X, -X, +Y, -Y, +Z, -Z
pip_config = {
    # Face +X (right): 1, 3, 5 pips
    '+X': {
        1: [(1.0, 0, 0)],
        3: [(1.0, -0.5, -0.5), (1.0, 0, 0), (1.0, 0.5, 0.5)],
        5: [(1.0, -0.6, -0.6), (1.0, -0.6, 0.6), (1.0, 0, 0), (1.0, 0.6, -0.6), (1.0, 0.6, 0.6)]
    },
    # Face -X (left): 6 pips
    '-X': {
        6: [(-1.0, -0.6, -0.6), (-1.0, -0.6, 0.6), (-1.0, -0.3, 0), (-1.0, 0.6, -0.6), (-1.0, 0.6, 0.6), (-1.0, 0.3, 0)]
    },
    # Face +Y (front): 2 pips
    '+Y': {
        2: [(0.6, 1.0, 0.6), (-0.6, 1.0, -0.6)]
    },
    # Face -Y (back): 4 pips
    '-Y': {
        4: [(0.6, -1.0, 0.6), (-0.6, -1.0, 0.6), (0.6, -1.0, -0.6), (-0.6, -1.0, -0.6)]
    },
    # Face +Z (top): 5 pips
    '+Z': {
        5: [(-0.6, -0.6, 1.0), (-0.6, 0.6, 1.0), (0, 0, 1.0), (0.6, -0.6, 1.0), (0.6, 0.6, 1.0)]
    },
    # Face -Z (bottom): 2 pips
    '-Z': {
        2: [(0.6, 0.6, -1.0), (-0.6, -0.6, -1.0)]
    }
}

# Create pips as small cylinders on each face
pip_radius = 0.12
pip_height = 0.15

for face_key, pips_dict in pip_config.items():
    for num_pips, positions in pips_dict.items():
        for pos in positions:
            # Create a small cylinder for each pip
            bpy.ops.mesh.primitive_cylinder_add(
                radius=pip_radius,
                depth=pip_height,
                vertices=8,
                location=pos
            )
            pip = bpy.context.active_object
            pip.name = f"Pip_{face_key}"
            
            # Orient cylinder based on face
            if face_key == '+X':
                pip.rotation_euler = (0, pi/2, 0)
            elif face_key == '-X':
                pip.rotation_euler = (0, pi/2, 0)
            elif face_key == '+Y':
                pip.rotation_euler = (pi/2, 0, 0)
            elif face_key == '-Y':
                pip.rotation_euler = (pi/2, 0, 0)
            elif face_key == '+Z':
                pass  # No rotation needed
            elif face_key == '-Z':
                pass  # No rotation needed

# Join all pips into a single object and then join with die
bpy.ops.object.select_all(action='DESELECT')
for obj in bpy.context.scene.objects:
    if obj.name.startswith("Pip_"):
        obj.select_set(True)

if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.object.join()
    pips = bpy.context.active_object
    pips.name = "Pips"

# Select die and pips to join them
bpy.ops.object.select_all(action='DESELECT')
die.select_set(True)
if 'pips' in locals():
    pips.select_set(True)
    bpy.context.view_layer.objects.active = die

# Join all objects
bpy.ops.object.join()
final_die = bpy.context.active_object
final_die.name = "Die_Complete"

# Apply smooth shading
bpy.context.view_layer.objects.active = final_die
bpy.ops.object.shade_smooth()

print("Die created successfully with rounded edges and pips")
