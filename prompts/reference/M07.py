# Hand-written reference solution (used by --smoke). Geometry Nodes scatter, Blender 4.x API.
import bpy

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.mesh.primitive_plane_add(size=4)
plane = bpy.context.active_object
plane.name = "Ground"

ng = bpy.data.node_groups.new("Scatter", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
n, l = ng.nodes, ng.links

gi = n.new("NodeGroupInput")
go = n.new("NodeGroupOutput")
dist = n.new("GeometryNodeDistributePointsOnFaces")
dist.distribute_method = "RANDOM"
dist.inputs["Density"].default_value = 12.5          # 16 m^2 * 12.5 = ~200 points
dist.inputs["Seed"].default_value = 3
ico = n.new("GeometryNodeMeshIcoSphere")
ico.inputs["Radius"].default_value = 0.06
ico.inputs["Subdivisions"].default_value = 2
inst = n.new("GeometryNodeInstanceOnPoints")
rscale = n.new("FunctionNodeRandomValue")
rscale.data_type = "FLOAT_VECTOR"
rscale.inputs[0].default_value = (0.5, 0.5, 0.4)
rscale.inputs[1].default_value = (1.5, 1.5, 1.0)
rrot = n.new("FunctionNodeRandomValue")
rrot.data_type = "FLOAT_VECTOR"
rrot.inputs[1].default_value = (6.283, 6.283, 6.283)
join = n.new("GeometryNodeJoinGeometry")

l.new(gi.outputs["Geometry"], dist.inputs["Mesh"])
l.new(dist.outputs["Points"], inst.inputs["Points"])
l.new(ico.outputs["Mesh"], inst.inputs["Instance"])
l.new(rscale.outputs["Value"], inst.inputs["Scale"])
l.new(rrot.outputs["Value"], inst.inputs["Rotation"])
l.new(gi.outputs["Geometry"], join.inputs["Geometry"])
l.new(inst.outputs["Instances"], join.inputs["Geometry"])
l.new(join.outputs["Geometry"], go.inputs["Geometry"])

mod = plane.modifiers.new("Scatter", "NODES")
mod.node_group = ng
