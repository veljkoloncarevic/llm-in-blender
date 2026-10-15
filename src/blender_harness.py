"""
Runs INSIDE Blender:
    blender -b --factory-startup -P blender_harness.py -- --script s.py --out DIR --settings settings.json

1. Starts from an empty scene.
2. Executes the LLM-generated script and records success / exception.
3. Collects scene statistics (evaluated geometry incl. modifiers and instances,
   modifiers, materials and shader-node graphs).
4. Replaces any cameras/lights with a fixed, identical rig and renders N views.

Always writes DIR/result.json (also on failure). DIR/exec_done marks that the
script itself finished, so a later timeout can be attributed to rendering.
"""
import json
import math
import sys
import time
import traceback

import bpy
import mathutils

argv = sys.argv[sys.argv.index("--") + 1:]
args = dict(zip(argv[0::2], argv[1::2]))
SCRIPT, OUT = args["--script"], args["--out"]
with open(args["--settings"]) as f:
    S = json.load(f)

GEOM_TYPES = {"MESH", "CURVE", "SURFACE", "META", "FONT"}
SOCKET_ALIASES = {
    "Transmission": ["Transmission Weight", "Transmission"],
    "Coat": ["Coat Weight", "Clearcoat"],
    "Metallic": ["Metallic"],
    "Roughness": ["Roughness"],
    "IOR": ["IOR"],
    "Emission Strength": ["Emission Strength"],
}

result = {"status": None, "blender_version": bpy.app.version_string}


def write_result():
    with open(f"{OUT}/result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)


# --------------------------------------------------------------------------- 1
# Start from Blender's default startup scene (cube, camera, light; --factory-startup),
# i.e. the scene a user would run the script in. Tag the startup objects so we can
# record whether the script actually removed them as instructed.
for _ob in bpy.data.objects:
    _ob["_harness_startup"] = True

# --------------------------------------------------------------------------- 2
with open(SCRIPT, encoding="utf-8") as f:
    code = f.read()
t0 = time.time()
try:
    compiled = compile(code, "llm_script.py", "exec")
    exec(compiled, {"__name__": "__main__", "__file__": "llm_script.py"})
    result["exec_ok"] = True
except KeyboardInterrupt:
    raise
except BaseException as e:  # incl. SystemExit called by the script
    result["exec_ok"] = False
    result["error_type"] = type(e).__name__
    result["error_message"] = str(e)[:2000]
    tb = traceback.extract_tb(e.__traceback__)
    llm_frames = [fr for fr in tb if fr.filename == "llm_script.py"]
    result["error_line"] = llm_frames[-1].lineno if llm_frames else getattr(e, "lineno", None)
    result["traceback"] = traceback.format_exc()[-4000:]
result["exec_time_s"] = round(time.time() - t0, 3)
open(f"{OUT}/exec_done", "w").close()

if not result["exec_ok"]:
    result["status"] = "exec_error"
    write_result()
    sys.exit(0)

# --------------------------------------------------------------------------- 3
try:
    scene = bpy.context.scene
    if scene is None:  # script deleted/replaced the scene
        scene = bpy.data.scenes[0]
        if bpy.context.window is not None:
            bpy.context.window.scene = scene
    vl = scene.view_layers[0]
    dg = scene.view_layers[0].depsgraph if bpy.context.scene is not scene else bpy.context.evaluated_depsgraph_get()
    dg.update()

    # ---- evaluated geometry, counting instances (geometry nodes, particles...)
    faces = tris = verts = 0
    mesh_cache = {}
    bb_min = mathutils.Vector((1e18,) * 3)
    bb_max = mathutils.Vector((-1e18,) * 3)
    for inst in dg.object_instances:
        ob = inst.object
        if ob.type not in GEOM_TYPES:
            continue
        # geometry-nodes instances share the instancer's name, so key on the data pointer
        key = (ob.name, ob.data.as_pointer() if ob.data is not None else ob.as_pointer())
        if key not in mesh_cache:
            try:
                me = ob.to_mesh()
                if me is None:
                    mesh_cache[key] = None
                else:
                    me.calc_loop_triangles()
                    nv = len(me.vertices)
                    step = nv // 2000 + 1   # subsample points for the bounding box
                    pts = [mathutils.Vector(me.vertices[i].co) for i in range(0, nv, step)]
                    mesh_cache[key] = (len(me.polygons), len(me.loop_triangles), nv, pts)
                    ob.to_mesh_clear()
            except RuntimeError:
                mesh_cache[key] = None
        stats = mesh_cache[key]
        if not stats:
            continue
        faces += stats[0]
        tris += stats[1]
        verts += stats[2]
        mw = inst.matrix_world
        for c in stats[3]:
            w = mw @ c
            for k in range(3):
                if w[k] < bb_min[k]:
                    bb_min[k] = w[k]
                if w[k] > bb_max[k]:
                    bb_max[k] = w[k]

    # ---- objects & modifiers
    objects = []
    for ob in scene.objects:
        if ob.type not in GEOM_TYPES:
            continue
        if not ob.visible_get(view_layer=vl):
            continue
        n_mat_on_faces = 0
        if ob.type == "MESH" and ob.data and len(ob.material_slots) > 1:
            idx = {p.material_index for p in ob.data.polygons}
            n_mat_on_faces = len({ob.material_slots[i].material.name for i in idx
                                  if i < len(ob.material_slots) and ob.material_slots[i].material})
        elif ob.material_slots and ob.material_slots[0].material:
            n_mat_on_faces = 1
        objects.append({
            "name": ob.name, "type": ob.type,
            "modifiers": [m.type for m in ob.modifiers],
            "materials": [s.material.name for s in ob.material_slots if s.material],
            "distinct_materials_on_faces": n_mat_on_faces,
        })
    assigned = {m for o in objects for m in o["materials"]}
    leftover = [ob.name for ob in scene.objects if ob.get("_harness_startup")]

    # ---- materials / shader graphs
    def input_value(node, names):
        for n in names:
            sock = node.inputs.get(n)
            if sock is not None:
                if sock.is_linked:
                    return "linked"
                v = sock.default_value
                try:
                    return float(v)
                except TypeError:
                    return list(v)
        return None

    materials = []
    for mat in bpy.data.materials:
        info = {"name": mat.name, "assigned": mat.name in assigned, "use_nodes": bool(mat.use_nodes)}
        if mat.use_nodes and mat.node_tree:
            nt = mat.node_tree
            outs = [n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial"]
            active = [n for n in outs if n.is_active_output] or outs[:1]
            upstream, stack = set(), list(active)
            while stack:
                n = stack.pop()
                if n.name in upstream:
                    continue
                upstream.add(n.name)
                for sock in n.inputs:
                    for link in sock.links:
                        if link.is_valid and not link.is_muted:
                            stack.append(link.from_node)
            conn = [nt.nodes[n] for n in upstream]
            ignorable = {"NodeFrame", "NodeReroute"}
            info.update({
                "n_nodes": len(nt.nodes), "n_links": len(nt.links),
                "node_types_all": sorted({n.bl_idname for n in nt.nodes}),
                "node_types_connected": sorted({n.bl_idname for n in conn}),
                "n_unconnected_nodes": sum(1 for n in nt.nodes
                                           if n.name not in upstream and n.bl_idname not in ignorable),
                "output_has_surface": bool(active and active[0].inputs["Surface"].is_linked),
                "principled": [{k: input_value(n, al) for k, al in SOCKET_ALIASES.items()}
                               for n in conn if n.bl_idname == "ShaderNodeBsdfPrincipled"],
                "emission_nodes": [input_value(n, ["Strength"]) for n in conn
                                   if n.bl_idname == "ShaderNodeEmission"],
            })
        materials.append(info)

    has_geom = faces > 0
    result["scene"] = {
        "faces": faces, "triangles": tris, "vertices": verts,
        "n_geometry_objects": len(objects),
        "objects": objects[:200], "objects_truncated": len(objects) > 200,
        "modifier_types": sorted({m for o in objects for m in o["modifiers"]}),
        "materials": materials,
        "n_materials_assigned": len(assigned),
        "startup_objects_left": leftover,
        "bbox_min": list(bb_min) if has_geom else None,
        "bbox_max": list(bb_max) if has_geom else None,
    }
except Exception as e:
    result["status"] = "analysis_error"
    result["error_type"], result["error_message"] = type(e).__name__, str(e)
    result["traceback"] = traceback.format_exc()[-4000:]
    write_result()
    sys.exit(0)

if not has_geom:
    result["status"] = "empty_scene"
    write_result()
    sys.exit(0)

# --------------------------------------------------------------------------- 4
try:
    R = S["render"]
    for ob in list(scene.objects):          # identical camera + lighting for every attempt
        if ob.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(ob, do_unlink=True)

    world = bpy.data.worlds.new("EvalWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.8, 0.8, 0.8, 1.0)
    bg.inputs["Strength"].default_value = 0.6
    scene.world = world

    for name, rot, energy in [("Key", (50, 0, 30), 3.0), ("Fill", (60, 0, -120), 1.0)]:
        ld = bpy.data.lights.new(name, "SUN")
        ld.energy = energy
        lo = bpy.data.objects.new(name, ld)
        lo.rotation_euler = [math.radians(a) for a in rot]
        scene.collection.objects.link(lo)

    cam_data = bpy.data.cameras.new("EvalCam")
    cam_data.lens = 50
    cam_data.clip_start = 0.001
    cam = bpy.data.objects.new("EvalCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    center = (bb_min + bb_max) / 2
    radius = max((bb_max - bb_min).length / 2, 1e-3)
    cam_data.clip_end = max(1000.0, radius * 20)
    fov = cam_data.angle
    dist = radius / math.sin(fov / 2) * 1.05

    r = scene.render
    r.engine = R["engine"]
    r.resolution_x = r.resolution_y = int(R["resolution"])
    r.resolution_percentage = 100
    r.film_transparent = False
    r.image_settings.file_format = "PNG"
    r.threads_mode = "FIXED"
    r.threads = int(S.get("threads", 2))
    if R["engine"] == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = int(R["samples"])
        scene.cycles.use_denoising = bool(R.get("denoise", True))
        scene.cycles.use_adaptive_sampling = True
    else:
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"

    views, t0 = [], time.time()
    for i, (az, el) in enumerate(R["views"]):
        a, e = math.radians(az), math.radians(el)
        off = mathutils.Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))
        cam.location = center + off * dist
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        path = f"{OUT}/view_{i}.png"
        r.filepath = path
        bpy.ops.render.render(write_still=True)
        views.append(f"view_{i}.png")
    result["render_time_s"] = round(time.time() - t0, 3)
    result["views"] = views
    result["status"] = "ok"
except Exception as e:
    result["status"] = "render_error"
    result["error_type"], result["error_message"] = type(e).__name__, str(e)
    result["traceback"] = traceback.format_exc()[-4000:]

write_result()
sys.exit(0)
