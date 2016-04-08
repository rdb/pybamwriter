
from .typed_objects import TypedWritableReferenceCount
from .texture import SamplerState, TextureStage, Texture
from .material import Material
from .render_states import TransformState


class RenderAttrib(TypedWritableReferenceCount):
    __slots__ = ()

class TransparencyAttrib(RenderAttrib):

    __slots__ = 'mode',

    M_none = 0
    M_alpha = 1
    M_notused = 2
    M_multisample = 3
    M_multisample_mask = 4
    M_binary = 5
    M_dual = 6

    def __init__(self, mode):
        super().__init__()

        self.mode = mode

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_int8(self.mode)

TransparencyAttrib.none = TransparencyAttrib(TransparencyAttrib.M_none)
TransparencyAttrib.alpha = TransparencyAttrib(TransparencyAttrib.M_alpha)
TransparencyAttrib.multisample_mask = TransparencyAttrib(TransparencyAttrib.M_multisample_mask)
TransparencyAttrib.binary = TransparencyAttrib(TransparencyAttrib.M_binary)


class ColorAttrib(RenderAttrib):

    __slots__ = 'type', 'color'

    T_vertex = 0
    T_flat = 1
    T_off = 2

    def __init__(self, type, color=(1, 1, 1, 1)):
        super().__init__()

        self.type = type
        self.color = color

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_int8(self.type)
        dg.add_vec4(self.color)

ColorAttrib.off = ColorAttrib(ColorAttrib.T_off)
ColorAttrib.vertex = ColorAttrib(ColorAttrib.T_vertex)


class MaterialAttrib(RenderAttrib):

    __slots__ = 'material',

    def __init__(self, material=None):
        super().__init__()

        self.material = material

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        assert isinstance(self.material, Material)
        manager.write_pointer(dg, self.material)


class TextureAttrib(RenderAttrib):

    # textureAttrib.h:StageNode
    class StageNode:

        def __init__(self):
            self.sampler = None
            self.stage = None
            self.texture = None
            self.ff_tc_index = 0
            self.implicit_sort = 0
            self.override = 0

    __slots__ = 'off_all_stages', 'off_stage_nodes', 'on_stage_nodes'

    def __init__(self):
        super().__init__()

        self.off_all_stages = False
        self.off_stage_nodes = []
        self.on_stage_nodes = []

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_bool(self.off_all_stages)
        dg.add_uint16(len(self.off_stage_nodes))

        for stage_node in self.off_stage_nodes:
            assert isinstance(stage_node, TextureAttrib.StageNode)
            assert isinstance(stage_node.stage, TextureStage)
            manager.write_pointer(dg, stage_node.stage)

        dg.add_uint16(len(self.on_stage_nodes))

        for stage_node in self.on_stage_nodes:
            assert isinstance(stage_node, TextureAttrib.StageNode)
            assert isinstance(stage_node.stage, TextureStage)
            assert isinstance(stage_node.texture, Texture)

            manager.write_pointer(dg, stage_node.stage)
            manager.write_pointer(dg, stage_node.texture)

            if manager.file_version >= (6, 15):
                dg.add_uint16(stage_node.implicit_sort)

            if manager.file_version >= (6, 23):
                dg.add_int32(stage_node.override)

            if manager.file_version >= (6, 36):
                dg.add_bool(True if stage_node.sampler else False)

                if stage_node.sampler:
                    assert isinstance(stage_node.sampler, SamplerState)
                    stage_node.sampler.write_datagram(manager, dg)


class TexMatrixAttrib(RenderAttrib):

    class StageNode:

        __slots__ = 'stage', 'transform', 'override'

        def __init__(self, stage=None, transform=None, override=0):
            self.stage = stage
            self.transform = transform
            self.override = override

    __slots__ = 'stages',

    def __init__(self):
        super().__init__()
        self.stages = []

    def add_stage(self, stage, transform, override):
        self.stages.append(self.StageNode(stage, transform, override))

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(len(self.stages))

        for stage_node in self.stages:
            assert isinstance(stage_node, TexMatrixAttrib.StageNode)
            assert isinstance(stage_node.stage, TextureStage)
            assert isinstance(stage_node.transform, TransformState)

            manager.write_pointer(dg, stage_node.stage)
            manager.write_pointer(dg, stage_node.transform)
            dg.add_int32(stage_node.override)


class CullFaceAttrib(RenderAttrib):

    M_cull_none = 0
    M_cull_clockwise = 1
    M_cull_counter_clockwise = 2
    M_cull_unchanged = 3

    __slots__ = 'mode', 'reverse'

    def __init__(self, mode, reverse=False):
        super().__init__()
        self.mode = mode
        self.reverse = reverse

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_int8(self.mode)
        dg.add_bool(self.reverse)

CullFaceAttrib.cull_none = CullFaceAttrib(CullFaceAttrib.M_cull_none)


class AntialiasAttrib(RenderAttrib):

    M_none        = 0x0000
    M_point       = 0x0001
    M_line        = 0x0002
    M_polygon     = 0x0004
    M_multisample = 0x0008
    M_auto        = 0x001f
    M_type_mask   = 0x001f

    M_faster      = 0x0020
    M_better      = 0x0040
    M_dont_care   = 0x0060

    __slots__ = 'mode',

    def __init__(self, mode):
        super().__init__()
        self.mode = mode

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(self.mode)

AntialiasAttrib.none = AntialiasAttrib(AntialiasAttrib.M_none)
AntialiasAttrib.multisample = AntialiasAttrib(AntialiasAttrib.M_multisample)


class ColorBlendAttrib(RenderAttrib):

    M_none = 0
    M_add = 1
    M_subtract = 2
    M_inv_subtract = 3
    M_min = 4
    M_max = 5

    __slots__ = 'mode', 'a', 'b', 'color', 'alpha_mode', 'alpha_a', 'alpha_b'

    def __init__(self, mode, a=1, b=1, color=(0, 0, 0, 0)):
        super().__init__()

        self.mode = mode
        self.a = 1
        self.b = 1
        self.color = color
        self.alpha_mode = self.mode
        self.alpha_a = self.a
        self.alpha_b = self.b

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint8(self.mode)
        dg.add_uint8(self.a)
        dg.add_uint8(self.b)

        if manager.file_version >= (6, 42):
            # Write alpha settings.
            dg.add_uint8(self.alpha_mode)
            dg.add_uint8(self.alpha_a)
            dg.add_uint8(self.alpha_b)

        dg.add_vec4(self.color)


ColorBlendAttrib.none = ColorBlendAttrib(ColorBlendAttrib.M_none)
ColorBlendAttrib.add = ColorBlendAttrib(ColorBlendAttrib.M_add)


class RenderModeAttrib(RenderAttrib):

    M_unchanged = 0
    M_filled = 1
    M_wireframe = 2
    M_point = 3
    M_filled_flat = 4
    M_filled_wireframe = 5

    __slots__ = 'mode', 'thickness', 'perspective', 'wireframe_color'

    def __init__(self, mode, thickness=1, perspective=False, wireframe_color=(0, 0, 0, 0)):
        super().__init__()

        self.mode = mode
        self.thickness = thickness
        self.perspective = perspective
        self.wireframe_color = wireframe_color

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_int8(self.mode)
        dg.add_stdfloat(self.thickness)
        dg.add_bool(self.perspective)

        if self.mode == RenderModeAttrib.M_filled_wireframe:
            dg.add_vec4(self.wireframe_color)

RenderModeAttrib.wireframe = RenderModeAttrib(RenderModeAttrib.M_wireframe, 1, False)


class LightAttrib(RenderAttrib):

    __slots__ = 'off_all_lights', 'off_lights', 'on_lights'

    def __init__(self):
        self.off_all_lights = False
        self.off_lights = set()
        self.on_lights = set()

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_bool(self.off_all_lights)

        dg.add_uint16(len(self.off_lights))
        for light in self.off_lights:
            if manager.file_version >= (6, 40):
                #TODO: support NodePath to support instanced lights
                manager.write_pointer(dg, light)
                manager.write_pointer(dg, None)
            else:
                manager.write_pointer(dg, light)

        dg.add_uint16(len(self.on_lights))
        for light in self.on_lights:
            if manager.file_version >= (6, 40):
                #TODO: support NodePath to support instanced lights
                manager.write_pointer(dg, light)
                manager.write_pointer(dg, None)
            else:
                manager.write_pointer(dg, light)


LightAttrib.off = LightAttrib()
LightAttrib.off.off_all_lights = True
