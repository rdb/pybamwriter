from panda_types import PandaNode, ModelRoot


if __name__ == '__main__':
    from bam_writer import BamWriter

    model = ModelRoot("test")

    child1 = PandaNode("childnode1")
    model.add_child(child1)

    child2 = PandaNode("childnode2")
    model.add_child(child2)

    writer = BamWriter()
    writer.open_file('test.bam')
    writer.write_object(model)
    writer.close()

    print("test.bam written")
