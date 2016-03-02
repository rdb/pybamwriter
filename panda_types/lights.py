from .panda_node import PandaNode

class Light:

    def __init__(self):
        self.color = (1, 1, 1, 1)
        self.color_temperature = None
        self.priority = 0

    def write_datagram(self, manager, dg):
        use_color_temp = False

        if manager.file_version >= (6, 39):
            use_color_temp = self.color_temperature is not None
            dg.add_bool(use_color_temp)

        if use_color_temp:
            dg.add_stdfloat(self.color_temperature)
        else:
            dg.add_vec4(self.color)

        dg.add_int32(self.priority)


class LightNode(Light, PandaNode):

    __slots__ = ()

    def __init__(self, name):
        PandaNode.__init__(self, name)
        Light.__init__(self)

    def write_datagram(self, manager, dg):
        PandaNode.write_datagram(self, manager, dg)
        Light.write_datagram(self, manager, dg)


class AmbientLight(LightNode):

    __slots__ = ()
