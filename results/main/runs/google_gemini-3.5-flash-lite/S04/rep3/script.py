import bpy

# Clear existing objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- 1. Create Ground Plane ---
bpy.ops.mesh.primitive_plane_size(size=10.0)
ground = bpy.context.active_object
ground.name = "GroundPlane"

# --- 2. Create Glass Sphere ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.5, segments=64, ring_count=32, location=(0, 0, 1.5))
sphere = bpy.context.active_object
sphere.name = "GlassSphere"

# Apply smooth shading to the sphere
for face in sphere.data.polygons:
    face.use_smooth = True

# --- 3. Create Materials ---

# Blue Ground Material
mat_ground = bpy.data.materials.new(name="BlueGroundMaterial")
mat_ground.use_nodes = True
nodes_ground = mat_ground.node_tree.nodes
bsdf_ground = nodes_ground.get("Principled BSDF")

if bsdf_ground:
    # Set a vibrant blue base color and slightly lower roughness
    bsdf_ground.inputs["Base Color"].default_value = (0.05, 0.2, 0.6, 1.0)
    bsdf_ground.inputs["Roughness"].default_value = 0.3

ground.data.materials.append(mat_ground)

# Clear Glass Material
mat_glass = bpy.data.materials.new(name="ClearGlassMaterial")
mat_glass.use_nodes = True
nodes_glass = mat_glass.node_tree.nodes
bsdf_glass = nodes_glass.get("Principled BSDF")

if bsdf_glass:
    # Configure Principled BSDF for clear glass
    bsdf_glass.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_glass.inputs["Roughness"].default_value = 0.02
    bsdf_glass.inputs["IOR"].default_value = 1.45
    bsdf_glass.inputs["Transmission Weight"].default_value = 1.0

sphere.data.materials.append(mat_glass)
