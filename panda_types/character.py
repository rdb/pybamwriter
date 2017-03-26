
from .typed_objects import TypedWritableReferenceCount, CopyOnWriteObject
from .panda_node import PandaNode
from .geom import VertexTransform


class PartBundleNode(PandaNode):

    def __init__(self, name, bundle):
        super().__init__(name)

        self.bundles = [bundle]

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if manager.file_version >= (6, 5):
            dg.add_uint16(len(self.bundles))
            for bundle in self.bundles:
                manager.write_pointer(dg, bundle)
        else:
            manager.write_pointer(dg, self.bundles[0])


class Character(PartBundleNode):

    __slots__ = '_joints',

    def __init__(self, name):
        super().__init__(name, CharacterJointBundle(name))

        self._joints = {}

    def find_joint(self, name):
        return self._joints.get(name)

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)
        dg.add_uint16(0)


class PartGroup(TypedWritableReferenceCount):

    def __init__(self, parent, name):
        super().__init__()

        if parent is not None:
            parent.children.append(self)

        self.name = name
        self.children = []

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_string(self.name)

        dg.add_uint16(len(self.children))
        for child in self.children:
            manager.write_pointer(dg, child)


class PartBundle(PartGroup):

    def __init__(self, name=""):
        super().__init__(None, name)

        self.blend_type = 1
        self.anim_blend_flag = False
        self.frame_blend_flag = False
        self.root_xform = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if manager.file_version >= (6, 17):
            # anim_preload
            manager.write_pointer(dg, None)

        dg.add_uint8(self.blend_type)
        dg.add_bool(self.anim_blend_flag)
        dg.add_bool(self.frame_blend_flag)

        for i in (0, 1, 2, 3):
            for j in (0, 1, 2, 3):
                dg.add_stdfloat(self.root_xform[j][i])


class CharacterJointBundle(PartBundle):
    pass


class MovingPartBase(PartGroup):

    def __init__(self, parent, name):
        super().__init__(parent, name)

        self.forced_channel = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if manager.file_version >= (6, 20):
            manager.write_pointer(dg, self.forced_channel)


class MovingPartMatrix(MovingPartBase):

    def __init__(self, parent, name, default_value):
        super().__init__(parent, name)

        self.value = default_value
        self.default_value = default_value

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        for i in (0, 1, 2, 3):
            for j in (0, 1, 2, 3):
                dg.add_stdfloat(self.value[j][i])

        for i in (0, 1, 2, 3):
            for j in (0, 1, 2, 3):
                dg.add_stdfloat(self.default_value[j][i])


class CharacterJoint(MovingPartMatrix):

    def __init__(self, character, root, parent, name, default_value):
        super().__init__(parent, name, default_value)

        character._joints[name] = self

        self.character = character
        self.initial_net_transform_inverse = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if manager.file_version >= (6, 4):
            manager.write_pointer(dg, self.character)

        dg.add_uint16(0) # net nodes
        dg.add_uint16(0) # local nodes

        for i in (0, 1, 2, 3):
            for j in (0, 1, 2, 3):
                dg.add_stdfloat(self.initial_net_transform_inverse[j][i])


class JointVertexTransform(VertexTransform):

    def __init__(self, joint):
        super().__init__()
        assert isinstance(joint, CharacterJoint)
        self.joint = joint

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        manager.write_pointer(dg, self.joint)

