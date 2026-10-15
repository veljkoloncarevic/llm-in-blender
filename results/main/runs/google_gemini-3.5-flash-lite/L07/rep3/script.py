import bpy
import bmesh
import math

def create_low_poly_rocket():
    # 1. Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # We will build everything in a single mesh using bmesh to keep it clean and low-poly
    mesh = bpy.data.meshes.new("RocketMesh")
    obj = bpy.data.objects.new("LowPolyRocket", mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    bm = bmesh.new()

    # 2. Rocket Body (Cylinder)
    # 8 segments keeps it low-poly and easy to align fins (8 is divisible by 4, but 120 deg for 3 fins means we can just rotate)
    # Let's use 6 segments for a stylized low-poly crystal/retro look, perfectly matching 3-fold symmetry!
    segments = 6
    radius = 0.8
    height = 3.0

    # Create cylinder body
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=height
    )

    # Shift body up so origin is at the bottom/base of the rocket
    for v in bm.verts:
        v.co.z += height / 2.0

    # 3. Rocket Nose Cone
    nose_height = 1.5
    nose_base_z = height
    
    # Create nose cone atop the body
    geom_nose = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=0.0,
        depth=nose_height
    )
    
    # Move nose cone up
    for v in geom_nose['verts']:
        v.co.z += nose_base_z + (nose_height / 2.0)

    # 4. Fins (3 fins, 120 degrees apart)
    # We create one fin geometry, then duplicate/rotate it 3 times.
    num_fins = 3
    for i in range(num_fins):
        angle = i * (2 * math.pi / num_fins)
        
        # Create a cube for the fin
        fin_bm = bmesh.new()
        bmesh.ops.create_cube(fin_bm, size=1.0)
        
        # Shape and position the cube to act as a fin
        # Scale: thin in X, long in Y (outward), tall in Z
        matrix_scale = mathutils.Matrix.Scale(0.15, 4, mathutils.Vector((1, 0, 0))) @ \
                       mathutils.Matrix.Scale(0.8, 4, mathutils.Vector((0, 1, 0))) @ \
                       mathutils.Matrix.Scale(1.2, 4, mathutils.Vector((0, 0, 1)))
        
        bmesh.ops.transform(fin_bm, matrix=matrix_scale, verts=fin_bm.verts)
        
        # Shift outward from center and slightly up from the base
        matrix_translate = mathutils.Matrix.Translation((radius - 0.1, 0.0, 0.6))
        bmesh.ops.transform(fin_bm, matrix=matrix_translate, verts=fin_bm.verts)
        
        # Rotate around Z axis for each fin position
        matrix_rot = mathutils.Matrix.Rotation(angle, 4, 'Z')
        bmesh.ops.transform(fin_bm, matrix=matrix_rot, verts=fin_bm.verts)
        
        # Merge fin geometry into main bmesh
        for v in fin_bm.verts:
            bm.verts.new(v.co)
        bm.verts.ensure_lookup_table()
        
        # Recreate faces for the added fin vertices (simplest is to just use bm.from_mesh later, 
        # but since we are in bmesh, let's append geometry properly)
        fin_bm.free()

    # Alternatively, cleaner bmesh primitive addition for fins:
    bm.clear() # Let's rebuild procedurally using cleaner transformations to avoid manual vertex indexing issues.
    
    # --- RE-BUILD WITH CLEAN BMESH APPROACH ---
    bm = bmesh.new()

    # Body
    body = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.8, radius2=0.8, depth=3.0)
    for v in body['verts']:
        v.co.z += 1.5

    # Nose
    nose = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.8, radius2=0.0, depth=1.5)
    for v in nose['verts']:
        v.co.z += 3.0 + 0.75

    # Fins (built directly via transformed cube creation)
    for i in range(3):
        angle = i * (2.0 * math.pi / 3.0)
        
        # Create cube
        fin = bmesh.ops.create_cube(bm, size=1.0)
        
        # Transform each fin: scale, translate outward, rotate
        mat_scale = mathutils.Matrix.Scale(0.1, 4, mathutils.Vector((1, 0, 0))) @ \
                    mathutils.Matrix.Scale(0.9, 4, mathutils.Vector((0, 1, 0))) @ \
                    mathutils.Matrix.Scale(1.2, 4, mathutils.Vector((0, 0, 1)))
        
        mat_pos = mathutils.Matrix.Translation((0.7, 0.0, 0.8))
        mat_rot = mathutils.Matrix.Rotation(angle, 4, 'Z')
        
        # Combined transformation matrix
        final_mat = mat_rot @ mat_pos @ mat_scale
        
        bmesh.ops.transform(bm, matrix=final_mat, verts=fin['verts'])

    # Remove interior/duplicate faces if any, merge by distance
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)

    # Finish up mesh
    bm.to_mesh(mesh)
    bm.free()

    # 5. Add a simple low-poly material for visual distinction
    mat = bpy.data.materials.new(name="RocketMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.15, 1.0)  # Retro red
        bsdf.inputs["Roughness"].default_value = 0.4
    obj.data.materials.append(mat)

    # Ensure smooth/flat shading appropriate for low-poly (flat)
    bpy.ops.object.shade_flat()

create_low_poly_rocket()
