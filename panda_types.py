
class TypedObject(object):
    bam_type_name = "TypedObject"


class TypedWritable(TypedObject):
    bam_type_name = "TypedWritable"

    def write_datagram(self, manager, dg):
        pass


class RenderState(TypedWritable):
    bam_type_name = "RenderState"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # For now, just write out the value for a state with no attribs
        dg.add_uint16(0)

RenderState.empty = RenderState()


class TransformState(TypedWritable):
    bam_type_name = "TransformState"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # For now, just write out the flags for the identity matrix.
        dg.add_uint32(0x00010005)

TransformState.identity = TransformState()


class RenderEffects(TypedWritable):
    bam_type_name = "RenderEffects"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # For now, just pretend there are 0 render effects.
        dg.add_uint16(0)

RenderEffects.empty = RenderEffects()


class PandaNode(TypedWritable):
    bam_type_name = "PandaNode"

    def __init__(self, name=""):
        self.name = name

        self.state = RenderState.empty
        self.transform = TransformState.identity
        self.effects = RenderEffects.empty

        self.draw_control_mask = 0
        self.draw_show_mask = 0xffffffff
        self.into_collide_mask = 0
        self.bounds_type = 0 # BT_default
        self.tags = {}

        self.parents = []
        self.children = []
        self.stashed = []

    def add_child(self, child):
        assert isinstance(child, PandaNode)
        assert child is not self

        self.children.append(child)
        child.parents.append(self)

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_string(self.name)

        manager.write_pointer(dg, self.state)
        manager.write_pointer(dg, self.transform)
        manager.write_pointer(dg, self.effects)

        dg.add_uint32(self.draw_control_mask)
        dg.add_uint32(self.draw_show_mask)
        dg.add_uint32(self.into_collide_mask)

        if manager.file_version >= (6, 19):
            dg.add_uint8(self.bounds_type)

        dg.add_uint32(len(self.tags))
        for key, value in self.tags.items():
            dg.add_string(key)
            dg.add_string(value)

        dg.add_uint16(len(self.parents))
        for parent in self.parents:
            manager.write_pointer(dg, parent)

        dg.add_uint16(len(self.children))
        for child in self.children:
            manager.write_pointer(dg, child)
            dg.add_int32(0) # sort

        dg.add_uint16(len(self.stashed))
        for stashed in self.stashed:
            manager.write_pointer(dg, stashed)
            dg.add_int32(0) # sort


class ModelNode(PandaNode):
    bam_type_name = "ModelNode"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint8(0) # PT_none
        dg.add_uint16(0)


class ModelRoot(ModelNode):
    bam_type_name = "ModelRoot"
