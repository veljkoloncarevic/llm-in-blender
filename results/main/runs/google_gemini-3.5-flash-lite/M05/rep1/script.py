import bpy
import bmesh
import math
import mathutils

# --- Cleanup Scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Parameters ---
cols = 10
rows = 10
hex_radius = 1.0
wall_gap = 0.1  # Gap between individual cells
extrusion_height = 2.0

# Geometry math for pointy-topped hexagons
# Width of pointy-topped hex = sqrt(3) * radius
# Height of pointy-topped hex = 2 * radius
dx = math.sqrt(3) * hex_radius
dy = 1.5 * hex_radius

# Create a new mesh and object for the honeycomb
mesh = bpy.data.meshes.new("HoneycombMesh")
obj = bpy.data.objects.new("HoneycombPanel", mesh)
bpy.context.collection.objects.link(obj)

# Use bmesh to construct geometry efficiently
bm = bmesh.new()

# To add a gap between cells while keeping them distinct, 
# we scale down each hex slightly from its center.
inner_radius = hex_radius - (wall_gap * 0.5)

for r in range(rows):
    # Offset alternating rows
    x_offset = (dx / 2.0) if (r % 2 == 1) else 0.0
    y_pos = r * dy
    
    for c in range(cols):
        x_pos = c * dx + x_offset
        
        # Build a single hexagonal prism using bmesh utility
        # bmesh.ops.create_cone creates a cone or cylinder. 
        # A 6-vertex cylinder acts as a hexagonal prism.
        geom = bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=6,
            radius1=inner_radius,
            radius2=inner_radius,
            depth=extrusion_height
        )
        
        # Collect created faces/verts for translation
        created_verts = [v for v in geom['verts']]
        
        # Move the hex prism to its grid position
        # Note: create_cone centers the cylinder at origin along Z, 
        # so we shift it up by half-height to rest on Z=0, and apply grid offsets.
        translation = mathutils.Vector((x_pos, y_pos, extrusion_height / 2.0))
        bmesh.ops.translate(bm, verts=created_verts, vec=translation)

# Finalize mesh
bm.to_mesh(mesh)
bm.free()

# Set smooth shading for clean appearance
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()

print("Procedural honeycomb panel generated successfully.")
