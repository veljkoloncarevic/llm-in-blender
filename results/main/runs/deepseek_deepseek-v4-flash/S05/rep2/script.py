import bpy

# Switch to object mode if needed, then delete all existing objects
if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Dark ground plane ---
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Dark_Ground"

ground_mat = bpy.data.materials.new("Ground_Material")
ground_mat.use_nodes = True
nt = ground_mat.node_tree
for node in nt.nodes:
    if node.type == 'BSDF_PRINCIPLED':
        node.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        node.inputs['Roughness'].default_value = 0.6
        break
ground.data.materials.append(ground_mat)

# --- Cyan neon ring (torus) ---
bpy.ops.mesh.primitive_torus_add(
    major_radius=1.0,
    minor_radius=0.05,
    location=(0, 0, 0.5),
)
ring = bpy.context.active_object
ring.name = "Neon_Cyan_Ring"

ring_mat = bpy.data.materials.new("Neon_Cyan_Material")
ring_mat.use_nodes = True
nt = ring_mat.node_tree

# Remove default nodes
for node in list(nt.nodes):
    nt.nodes.remove(node)

# Create emission shader
emission = nt.nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 1.0, 1.0, 1.0)
emission.inputs['Strength'].default_value = 5.0
output = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(emission.outputs[0], output.inputs['Surface'])

ring.data.materials.append(ring_mat)

# Smooth shading on the ring
bpy.ops.object.select_all(action='DESELECT')
ring.select_set(True)
bpy.context.view_layer.objects.active = ring
bpy.ops.object.shade_smooth()
