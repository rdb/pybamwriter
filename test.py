from .panda_types import *
from array import array

if __name__ == '__main__':
    from .bam_writer import BamWriter

    model = ModelRoot("test")

    child1 = PandaNode("childnode1")
    model.add_child(child1)

    child1.transform = TransformState()
    child1.transform.scale = (2, 2, 2)
    child1.transform.hpr = (90, 0, 180)
    child1.state = RenderState()
    child1.state.attributes.append(TransparencyAttrib())

    material = Material("My Material")
    material.diffuse = (0.2, 0.6, 1.0, 1.0)

    material_attrib = MaterialAttrib()
    material_attrib.material = material
    child1.state.attributes.append(material_attrib)

    texture_attrib = TextureAttrib()
    texture = Texture("My Texture")
    texture_stage = TextureStage.default
    sampler_state = SamplerState()
    stage_node = TextureAttrib.StageNode()
    stage_node.sampler = sampler_state
    stage_node.stage = texture_stage
    stage_node.texture = texture
    texture_attrib.on_stage_nodes.append(stage_node)

    child1.state.attributes.append(texture_attrib)

    array_format = GeomVertexArrayFormat()
    array_format.stride = 3 * 4 * 2
    array_format.total_bytes = 3 * 4 * 2
    array_format.pad_to = 4
    array_format.add_column("vertex", 3, GeomEnums.NT_float32,
                            GeomEnums.C_point, start=0, column_alignment=4)
    array_format.add_column("normal", 3, GeomEnums.NT_float32,
                            GeomEnums.C_point, start=4 * 3, column_alignment=4)

    array_data = GeomVertexArrayData(array_format, GeomEnums.UH_static)
    array_data.buffer += array('f', [0, 0, 0, 0, 1 ,0,
                                     0, 0, 1, 0, 1, 0,
                                    -1, 0, 1, 0, 1, 0])

    vertex_format = GeomVertexFormat(array_format)
    data = GeomVertexData("triangle", vertex_format, GeomEnums.UH_static)
    data.arrays.append(array_data)

    primitive = GeomTriangles(GeomEnums.UH_static)
    primitive.first_vertex = 0
    primitive.num_vertices = 3

    geom = Geom(data)
    geom.primitives.append(primitive)

    child2 = GeomNode("childnode2")
    child2.add_geom(geom)

    child2.state = RenderState(ColorAttrib(ColorAttrib.T_flat, (1.0, 0.6, 0.1, 1.0)))

    model.add_child(child2)

    child2.transform = TransformState()
    child2.transform.pos = (1, 0, 0)

    writer = BamWriter()
    writer.open_file('test.bam')
    writer.write_object(model)
    writer.close()

    print("test.bam written")
