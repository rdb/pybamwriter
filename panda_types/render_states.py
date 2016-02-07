
from .typed_objects import NodeCachedReferenceCount


class RenderState(NodeCachedReferenceCount):

    __slots__ = 'attributes',

    def __init__(self, *args):
        super().__init__()

        self.attributes = list(args)

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(len(self.attributes))
        for attrib in self.attributes:
            manager.write_pointer(dg, attrib)
            dg.add_int32(0) # Render attrib override

RenderState.empty = RenderState()


class TransformState(NodeCachedReferenceCount):

    __slots__ = 'pos', 'quat', 'hpr', 'scale', 'shear', 'mat'

    def __init__(self):
        super().__init__()
        self.pos = None
        self.quat = None
        self.hpr = None
        self.scale = None
        self.shear = None
        self.mat = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if self.pos or self.quat or self.hpr or self.scale or self.shear:
            if self.quat:
                dg.add_uint32(0x00000338)
            else:
                dg.add_uint32(0x00000c38)

            dg.add_vec3(self.pos or (0, 0, 0))

            if self.quat:
                dg.add_vec4(self.quat)
            else:
                dg.add_vec3(self.hpr or (0, 0, 0))

            dg.add_vec3(self.scale or (1, 1, 1))
            dg.add_vec3(self.shear or (0, 0, 0))

        elif self.mat:
            dg.add_uint32(0x00000040)

            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.mat[j][i])

        else:
            # Identity transform.
            dg.add_uint32(0x00010005)


TransformState.identity = TransformState()
