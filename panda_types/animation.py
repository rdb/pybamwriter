
from .typed_objects import TypedWritableReferenceCount, CopyOnWriteObject
from .panda_node import PandaNode


class AnimBundleNode(PandaNode):

    def __init__(self, name, bundle):
        super().__init__(name)

        self.bundle = bundle

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        manager.write_pointer(dg, self.bundle)


class AnimGroup(TypedWritableReferenceCount):

    def __init__(self, parent, name):
        super().__init__()

        if parent is not None:
            parent.children.append(self)
            self.root = parent.root
        else:
            self.root = self

        self.name = name
        self.children = []

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_string(self.name)

        manager.write_pointer(dg, self.root)

        dg.add_uint16(len(self.children))
        for child in self.children:
            manager.write_pointer(dg, child)


class AnimBundle(AnimGroup):

    def __init__(self, name, fps, num_frames):
        super().__init__(None, name)

        self.fps = fps
        self.num_frames = num_frames

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_stdfloat(self.fps)
        dg.add_uint16(self.num_frames)


class AnimChannelBase(AnimGroup):

    def __init__(self, parent, name):
        super().__init__(parent, name)

        self.last_frame = -1

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(self.last_frame & 0xffff)


class AnimChannelMatrix(AnimChannelBase):
    pass


class AnimChannelMatrixXfmTable(AnimChannelMatrix):

    def __init__(self, parent, name):
        super().__init__(parent, name)

        self.tables = [[] for _ in range(12)]

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_bool(False) # compress_channels
        dg.add_bool(True) # new HPR conventions

        assert len(self.tables) == 12

        add_stdfloat = dg.add_stdfloat
        for table in self.tables:
            dg.add_uint16(len(table))
            for entry in table:
                add_stdfloat(entry)
