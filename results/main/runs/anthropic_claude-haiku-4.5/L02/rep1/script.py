import bpy
import math
from mathutils import Vector

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create material for snowman body (white)
white_mat = bpy.data.materials.new(name="Snow")
white_mat.use_nodes = True
white_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)

# Create material for eyes (black)
black_mat = bpy.data.materials.new(name="Eyes")
black_mat.use_nodes = True
black_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

# Create material for carrot nose (orange)
orange_mat = bpy.data.materials.new(name="Carrot")
orange_mat.use_nodes = True
orange_mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (1.0, 0.5, 0.0, 1.0)

# Bottom sphere (largest)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.0), segments=16, ring_count=8)
bottom_sphere = bpy.context.active_object
bottom_sphere.data.materials.append(white_mat)

# Middle sphere (medium)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0, 2.65), segments=16, ring_count=8)
middle_sphere = bpy.context.active_object
middle_sphere.data.materials.append(white_mat)

# Top sphere (smallest)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 0, 3.95), segments=16, ring_count=8)
top_sphere = bpy.context.active_object
top_sphere.data.materials.append(white_mat)

# Carrot nose (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.0, depth=0.4, vertices=8, location=(0.4, 0, 3.95), rotation=(0, math.pi/2, 0))
carrot = bpy.context.active_object
carrot.data.materials.append(orange_mat)

# Left eye
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(-0.15, 0.35, 4.15), segments=8, ring_count=4)
left_eye = bpy.context.active_object
left_eye.data.materials.append(black_mat)

# Right eye
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0.15, 0.35, 4.15), segments=8, ring_count=4)
right_eye = bpy.context.active_object
right_eye.data.materials.append(black_mat)

# Select all and set origin to world origin for better viewing
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
