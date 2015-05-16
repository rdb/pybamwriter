
from .typed_objects import TypedWritable
from .render_states import RenderState, TransformState
from .render_effects import RenderEffects

class PandaNode(TypedWritable):

    def __init__(self, name=""):
        super().__init__()
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

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint8(0) # PT_none
        dg.add_uint16(0)

class ModelRoot(ModelNode):
    pass
