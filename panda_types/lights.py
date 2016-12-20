
from .panda_node import PandaNode, LensNode, Camera

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


class LightLensNode(Camera, Light):

    __slots__ = ('shadow_caster', 'sb_xsize', 'sb_ysize', 'sb_sort')

    def __init__(self, name="", lens=None):
        Light.__init__(self)
        Camera.__init__(self, name, lens)
        self.shadow_caster = False
        self.sb_xsize = 512
        self.sb_ysize = 512
        self.sb_sort = -10

    def write_datagram(self, manager, dg):
        Camera.write_datagram(self, manager, dg)
        Light.write_datagram(self, manager, dg)

        dg.add_bool(self.shadow_caster)
        dg.add_int32(self.sb_xsize)
        dg.add_int32(self.sb_ysize)
        dg.add_int32(self.sb_sort)

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

class PointLight(LightLensNode):

    __slots__ = ('specular_color', 'attenuation', 'point')

    def __init__(self, name=""):
        LightLensNode.__init__(self, name, None)
        self.has_specular_color = False
        self.specular_color = (0, 0, 0, 0)
        self.attenuation = (0, 0, 0)
        self.point = (0, 0, 0)
        self.max_distance = 30.0

    def write_datagram(self, manager, dg):
        LightLensNode.write_datagram(self, manager, dg)

        if manager.file_version >= (6, 39):
            dg.add_bool(self.has_specular_color)

        dg.add_vec4(self.specular_color)
        dg.add_vec3(self.attenuation)

        if manager.file_version >= (6, 41):
            dg.add_stdfloat(self.max_distance)

        dg.add_vec3(self.point)

class Spotlight(LightLensNode):

    def __init__(self, name=""):
        LightLensNode.__init__(self, name, None)
        self.has_specular_color = False
        self.exponent = 50.0
        self.specular_color = (0, 0, 0, 0)
        self.attenuation = (0, 0, 0)
        self.max_distance = 30.0

    def write_datagram(self, manager, dg):
        LightLensNode.write_datagram(self, manager, dg)

        if manager.file_version >= (6, 39):
            dg.add_bool(self.has_specular_color)

        dg.add_stdfloat(self.exponent)
        dg.add_vec4(self.specular_color)
        dg.add_vec3(self.attenuation)

        if manager.file_version >= (6, 41):
            dg.add_stdfloat(self.max_distance)

class SphereLight(PointLight):

    __slots__ = ('radius')

    def __init__(self, name=""):
        PointLight.__init__(self, name)
        self.radius = 0.01

    def write_datagram(self, manager, dg):
        PointLight.write_datagram(self, manager, dg)
        dg.add_stdfloat(self.radius)

class RectangleLight(LightLensNode):

    __slots__ = ('max_distance')

    def __init__(self, name=""):
        LightLensNode.__init__(self, name)
        self.max_distance = 30.0

    def write_datagram(self, manager, dg):
        LightLensNode.write_datagram(self, manager, dg)
        dg.add_stdfloat(self.max_distance)
