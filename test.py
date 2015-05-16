from .panda_types import *

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

    color_attrib = ColorAttrib()
    color_attrib.color = (1.0, 0.6, 0.1, 1.0)
    child1.state.attributes.append(color_attrib)

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


    child2 = GeomNode("childnode2")
    model.add_child(child2)

    child2.transform = TransformState()
    child2.transform.pos = (1, 0, 0)

    writer = BamWriter()
    writer.open_file('test.bam')
    writer.write_object(model)
    writer.close()

    print("test.bam written")
