"""Evaluates the per-prompt structural checks on a harness result.json."""


def _assigned_materials(scene):
    return [m for m in scene.get("materials", []) if m.get("assigned") and m.get("use_nodes")]


def _connected_types(scene):
    return {t for m in _assigned_materials(scene) for t in m.get("node_types_connected", [])}


def _ge(v, threshold):
    return v == "linked" or (isinstance(v, (int, float)) and v >= threshold)


def run_check(check, scene):
    t = check["type"]
    if t == "face_range":
        return check["min"] <= scene["faces"] <= check["max"]
    if t == "min_objects":
        return scene["n_geometry_objects"] >= check["n"]
    if t == "modifier_any":
        return bool(set(check["types"]) & set(scene.get("modifier_types", [])))
    if t == "min_materials":
        return sum(1 for m in _assigned_materials(scene) if m.get("output_has_surface")) >= check["n"]
    if t == "nodes_connected_all":
        return set(check["nodes"]) <= _connected_types(scene)
    if t == "nodes_connected_any":
        return bool(set(check["nodes"]) & _connected_types(scene))
    if t == "principled_min":
        return any(_ge(p.get(check["input"]), check["value"])
                   for m in _assigned_materials(scene) for p in m.get("principled", []))
    if t == "emissive":
        thr = check["min_strength"]
        for m in _assigned_materials(scene):
            if any(_ge(v, thr) for v in m.get("emission_nodes", [])):
                return True
            if any(_ge(p.get("Emission Strength"), thr) for p in m.get("principled", [])):
                return True
        return False
    if t == "multi_material_object":
        return any(o.get("distinct_materials_on_faces", 0) >= check["n"] for o in scene["objects"])
    raise ValueError(f"unknown check type {t}")


def evaluate(prompt, result):
    """Returns dict with per-check outcomes. Checks only apply to executed scenes."""
    scene = result.get("scene")
    if not scene:
        return {"checks": {}, "all_checks_pass": None, "poly_budget_ok": None}
    out = {}
    for i, c in enumerate(prompt["checks"]):
        out[f"{i}:{c['type']}"] = bool(run_check(c, scene))
    poly = [run_check(c, scene) for c in prompt["checks"] if c["type"] == "face_range"]
    material_types = {"min_materials", "nodes_connected_all", "nodes_connected_any",
                      "principled_min", "emissive", "multi_material_object"}
    mats = [run_check(c, scene) for c in prompt["checks"] if c["type"] in material_types]
    return {
        "checks": out,
        "all_checks_pass": all(out.values()),
        "check_pass_fraction": sum(out.values()) / len(out) if out else None,
        "poly_budget_ok": all(poly) if poly else None,
        "material_checks_ok": all(mats) if mats else None,
    }
