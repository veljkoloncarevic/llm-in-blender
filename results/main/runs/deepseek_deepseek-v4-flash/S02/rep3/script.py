import bpy

def clear_scene():
    """Remove all existing objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def create_floor():
    """Create a floor plane with a black-and-white checker texture as Base Color."""
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    floor = bpy.context.active_object

    mat = bpy.data.materials.new("FloorChecker")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    principled = nodes.get("Principled BSDF")
    checker = nodes.new("ShaderNodeTexChecker")
    checker.inputs["Scale"].default_value = 5.0

    # Checker defaults are black and white, connect to Base Color
    links.new(checker.outputs["Color"], principled.inputs["Base Color"])

    floor.data.materials.append(mat)
    return floor

def create_cube():
    """Create a glossy red cube sitting on the floor plane."""
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
    cube = bpy.context.active_object

    mat = bpy.data.materials.new("RedGlossy")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.8, 0.0, 0.0, 1.0)
    principled.inputs["Roughness"].default_value = 0.1

    cube.data.materials.append(mat)
    return cube

def main():
    clear_scene()
    create_floor()
    create_cube()

if __name__ == "__main__":
    main()
