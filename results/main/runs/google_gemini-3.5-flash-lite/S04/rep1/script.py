import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Create Ground Plane ---
bpy.ops.mesh.primitive_plane_size = 20.0
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground_plane = bpy.context.active_object
ground_plane.name = "GroundPlane"

# --- Create Blue Material for Ground Plane ---
ground_mat = bpy.data.materials.new(name="BlueGroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_links = ground_mat.node_tree.links

# Configure Principled BSDF for the ground
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.02, 0.15, 0.4, 1.0)  # Rich blue
    ground_bsdf.inputs['Roughness'].default_value = 0.2  # Slight gloss for reflections

ground_plane.data.materials.append(ground_mat)

# --- Create Glass Sphere ---
# Radius of 2.0, positioned so it rests perfectly on the z=0 plane
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2.0, 
    segments=64, 
    ring_count=32, 
    location=(0, 0, 2.0)
)
glass_sphere = bpy.context.active_object
glass_sphere.name = "GlassSphere"

# Smooth shading for the sphere
for face in glass_sphere.data.polygons:
    face.use_smooth = True

# --- Create Clear Glass Material ---
glass_mat = bpy.data.materials.new(name="ClearGlassMaterial")
glass_mat.use_nodes = True
glass_nodes = glass_mat.node_tree.nodes

# Configure Principled BSDF for clear glass
glass_bsdf = glass_nodes.get("Principled BSDF")
if glass_bsdf:
    glass_bsdf.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    glass_bsdf.inputs['Roughness'].default_value = 0.01      # Near 0 roughness
    glass_bsdf.inputs['Transmission Weight'].default_value = 1.0  # Full transmission
    glass_bsdf.inputs['IOR'].default_value = 1.45             # Glass IOR
    
    # Optional: ensure specular is set nicely for glass reflections
    if 'Specular IOR Level' in glass_bsdf.inputs:
        glass_bsdf.inputs['Specular IOR Level'].default_value = 0.5

glass_sphere.data.materials.append(glass_mat)
