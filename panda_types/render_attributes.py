 
from .typed_objects import TypedWritableReferenceCount
from .texture import SamplerState, TextureStage, Texture
from .material import Material


class RenderAttrib(TypedWritableReferenceCount):
    pass

class TransparencyAttrib(RenderAttrib):

    M_none = 0
    M_alpha = 1
    M_notused = 2
    M_multisample = 3
    M_multisample_mask = 4
    M_binary = 5
    M_dual = 6

    def __init__(self):
        super().__init__()

        self.mode = self.M_none

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_int8(self.mode)


class ColorAttrib(RenderAttrib):

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

    def __init__(self):
        super().__init__()

        self.material = None

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
