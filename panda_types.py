
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

    def __init__(self):
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

            pos = self.pos or (0, 0, 0)
            dg.add_stdfloat(pos[0])
            dg.add_stdfloat(pos[1])
            dg.add_stdfloat(pos[2])

            if self.quat:
                dg.add_stdfloat(self.quat[0])
                dg.add_stdfloat(self.quat[1])
                dg.add_stdfloat(self.quat[2])
                dg.add_stdfloat(self.quat[3])
            else:
                hpr = self.hpr or (0, 0, 0)
                dg.add_stdfloat(hpr[0])
                dg.add_stdfloat(hpr[1])
                dg.add_stdfloat(hpr[2])

            scale = self.scale or (1, 1, 1)
            dg.add_stdfloat(scale[0])
            dg.add_stdfloat(scale[1])
            dg.add_stdfloat(scale[2])

            shear = self.shear or (0, 0, 0)
            dg.add_stdfloat(shear[0])
            dg.add_stdfloat(shear[1])
            dg.add_stdfloat(shear[2])

        elif self.mat:
            dg.add_uint32(0x00000040)

            #TODO: check if this is the correct ordering
            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.mat[i][j])

        else:
            # Identity transform.
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


class GeomNode(PandaNode):
    bam_type_name = "GeomNode"

    def __init__(self, name):
        super().__init__(name)

        self.geoms = []

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(len(self.geoms))

        for geom in self.geoms:
            manager.write_pointer(dg, geom)


class ModelNode(PandaNode):
    bam_type_name = "ModelNode"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint8(0) # PT_none
        dg.add_uint16(0)


class ModelRoot(ModelNode):
    bam_type_name = "ModelRoot"
