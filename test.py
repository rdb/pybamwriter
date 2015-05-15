
from panda_types import  PandaNode, ModelRoot, TransformState, GeomNode

if __name__ == '__main__':
    from bam_writer import BamWriter

    model = ModelRoot("test")

    child1 = PandaNode("childnode1")
    model.add_child(child1)

    child1.transform = TransformState()
    child1.transform.scale = (2, 2, 2)
    child1.transform.hpr = (90, 0, 180)

    child2 = GeomNode("childnode2")
    model.add_child(child2)

    child2.transform = TransformState()
    child2.transform.pos = (1, 0, 0)

    writer = BamWriter()
    writer.open_file('test.bam')
    writer.write_object(model)
    writer.close()

    print("test.bam written")
