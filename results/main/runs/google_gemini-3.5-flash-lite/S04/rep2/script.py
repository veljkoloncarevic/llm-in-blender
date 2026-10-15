import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Create Ground Plane ---
bpy.ops.mesh.primitive_plane_size = 20.0
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, 0))
ground_plane = bpy.context.active_object
ground_plane.name = "GroundPlane"

# --- Create Ground Material (Blue) ---
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_links = ground_mat.node_tree.links

# Configure Principled BSDF for the ground
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs["Base Color"].default_value = (0.05, 0.15, 0.4, 1.0)  # Rich blue
    ground_bsdf.inputs["Roughness"].default_value = 0.3

ground_plane.data.materials.append(ground_mat)

# --- Create Glass Sphere ---
sphere_radius = 2.0
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=sphere_radius, 
    segments=64, 
    ring_count=32, 
    location=(0, 0, sphere_radius)
)
glass_sphere = bpy.context.active_object
glass_sphere.name = "GlassSphere"

# Smooth shading for the sphere
for face in glass_sphere.data.polygons:
    face.use_smooth = True

# --- Create Glass Material ---
glass_mat = bpy.data.materials.new(name="GlassMaterial")
glass_mat.use_nodes = True
glass_nodes = glass_mat.node_tree.nodes

# Configure Principled BSDF for clear glass
glass_bsdf = glass_nodes.get("Principled BSDF")
if glass_bsdf:
    glass_bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    glass_bsdf.inputs["Roughness"].default_value = 0.02
    glass_bsdf.inputs["IOR"].default_value = 1.45
    glass_bsdf.inputs["Weight"].default_value = 1.0  # Transmission Weight (Blender 4.X)
    
    # In Blender 4.0+, Transmission is controlled via the 'Transmission Weight' input
    if "Transmission Weight" in glass_bsdf.inputs:
        glass_bsdf.inputs["Transmission Weight"].default_value = 1.0
    elif "Transmission" in glass_bsdf.inputs: # Fallback for slightly older versions
        glass_bsdf.inputs["Transmission"].default_value = 1.0

glass_sphere.data.materials.append(glass_mat)
