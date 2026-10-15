import bpy
import bmesh
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 1. Model the Mug Body (Cylinder + Solidify) ---
# Create an open-topped cylinder (depth=2.0, radius=1.0)
bpy.ops.mesh.primitive_cylinder_add(
    radius=1.0,
    depth=2.0,
    vertices=32,
    end_fill_type='NOTHING',
    location=(0, 0, 1.0)
)
mug_obj = bpy.context.active_object
mug_obj.name = "CoffeeMug"

# Create a bottom face so the solidify modifier has something to thicken inward/outward properly
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mug_obj.data)

# Find boundary loops (the bottom and top edges)
# Since we created it with no caps, we select all boundary edges and bridge/fill the bottom
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()

# Collect boundary edges (edges with only 1 link face)
boundary_edges = [e for e in bm.edges if not e.is_manifold]

# Separate top and bottom boundaries based on Z coordinate
bottom_edges = [e for e in boundary_edges if all(v.co.z < 0.1 for v in e.verts)]

if bottom_edges:
    # Fill the bottom loop to create a closed base loop for the open cylinder
    # Or more robustly: select bottom boundary and fill (grid fill or face from verts)
    for e in bottom_edges:
        e.select = True
    # Use bmesh to make a face from the bottom boundary
    # Find the vert loop of the bottom boundary
    bottom_verts = []
    for e in bottom_edges:
        for v in e.verts:
            if v not in bottom_verts:
                bottom_verts.append(v)
    # Sort or just create a face if simple, but bmesh.ops.holes_fill works well for boundaries
    bmesh.ops.holes_fill(bm, edges=bottom_edges)

bpy.ops.object.mode_set(mode='OBJECT')

# Add Solidify modifier to give the mug thickness
solidify_mod = mug_obj.modifiers.new(name="Solidify", type='SOLIDIFY')
solidify_mod.thickness = 0.15
solidify_mod.offset = 1.0  # Thicken inwards/outwards cleanly
solidify_mod.use_quality_normals = True

# --- 2. Model the Mug Handle (Half Torus) ---
# Create a torus for the handle
bpy.ops.mesh.primitive_torus_add(
    major_radius=0.4,
    minor_radius=0.1,
    major_segments=24,
    minor_segments=12,
    location=(1.0, 0, 1.0),
    rotation=(0, math.radians(90), 0)
)
handle_obj = bpy.context.active_object
handle_obj.name = "MugHandle"

# Cut the torus in half to make a loop handle (delete half the geometry)
bpy.ops.object.mode_set(mode='EDIT')
bm_handle = bmesh.from_edit_mesh(handle_obj.data)
bm_handle.verts.ensure_lookup_table()

# Delete vertices on the negative X side (local to torus, or world X < 0.8)
verts_to_delete = [v for v in bm_handle.verts if v.co.x < 1.0]
bmesh.ops.delete(bm_handle, geom=verts_to_delete, context='VERTS')

bpy.ops.object.mode_set(mode='OBJECT')

# --- 3. Join Mug and Handle into a Single Mesh ---
mug_obj.select_set(True)
handle_obj.select_set(True)
bpy.context.view_layer.objects.active = mug_obj
bpy.ops.object.join()

# Final smooth shading and auto smooth for clean look
bpy.ops.object.shade_smooth()
