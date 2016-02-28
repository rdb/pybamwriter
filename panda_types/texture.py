
from .typed_objects import TypedWritableReferenceCount
from .geom import GeomEnums

class SamplerState(object):

    FT_nearest = 0
    FT_linear = 1
    FT_nearest_mipmap_nearest = 2
    FT_linear_mipmap_nearest = 3
    FT_nearest_mipmap_linear = 4
    FT_linear_mipmap_linear = 5
    FT_shadow = 6
    FT_default = 7

    WM_clamp = 0
    WM_repeat = 1
    WM_mirror = 2
    WM_mirror_once = 3
    WM_border_color = 4

    def __init__(self):
        self.wrap_u = self.WM_clamp
        self.wrap_v = self.WM_clamp
        self.wrap_w = self.WM_clamp
        self.minfilter = self.FT_linear
        self.magfilter = self.FT_linear
        self.anisotropic_degree = 0
        self.border_color = (0, 0, 0, 1)
        self.min_lod = -1000.0
        self.max_lod = 1000.0
        self.lod_bias = 0.0

    def write_datagram(self, manager, dg):

        dg.add_uint8(self.wrap_u)
        dg.add_uint8(self.wrap_v)
        dg.add_uint8(self.wrap_w)
        dg.add_uint8(self.minfilter)
        dg.add_uint8(self.magfilter)
        dg.add_int16(self.anisotropic_degree)
        dg.add_vec4(self.border_color)

        if manager.file_version >= (6, 36):
            dg.add_stdfloat(self.min_lod)
            dg.add_stdfloat(self.max_lod)
            dg.add_stdfloat(self.lod_bias)


class TextureStage(TypedWritableReferenceCount):

    M_modulate = 0
    M_decal = 1
    M_blend = 2
    M_replace = 3
    M_add = 4
    M_combine = 5
    M_blend_color_scale = 6
    M_modulate_glow = 7
    M_modulate_gloss = 8
    M_normal = 9
    M_normal_height = 10
    M_glow = 11
    M_gloss = 12
    M_height = 13
    M_selector = 14
    M_normal_gloss = 15

    CM_undefined = 0
    CM_replace = 1
    CM_modulate = 2
    CM_add = 3
    CM_add_signed = 4
    CM_interpolate = 5
    CM_subtract = 6

    CS_undefined = 0
    CS_texture = 1
    CS_constant = 2
    CS_primary_color = 3
    CS_previous = 4
    CS_constant_color_scale = 5
    CS_last_saved_result = 6

    CO_undefined = 0
    CO_src_color = 1
    CO_one_minus_src_color = 2
    CO_src_alpha = 3
    CO_one_minus_src_alpha = 4

    def __init__(self, name='Stage'):
        super().__init__()
        self.default = False
        self.name = name
        self.sort = 0
        self.priority = 0

        self.texcoord_name = 'texcoord'
        self.mode = self.M_modulate
        self.color = (1, 1, 1, 1)
        self.rgb_scale = 1
        self.alpha_scale = 1
        self.saved_result = False
        self.tex_view_offset = 0

        self.combine_rgb_mode = self.CM_undefined
        self.num_combine_rgb_operands = 0
        self.combine_rgb_source0 = self.CS_undefined
        self.combine_rgb_operand0 = self.CO_undefined
        self.combine_rgb_source1 = self.CS_undefined
        self.combine_rgb_operand1 = self.CO_undefined
        self.combine_rgb_source2 = self.CS_undefined
        self.combine_rgb_operand2 = self.CO_undefined

        self.combine_alpha_mode = self.CM_undefined
        self.num_combine_alpha_operands = 0
        self.combine_alpha_source0 = self.CS_undefined
        self.combine_alpha_operand0 = self.CO_undefined
        self.combine_alpha_source1 = self.CS_undefined
        self.combine_alpha_operand1 = self.CO_undefined
        self.combine_alpha_source2 = self.CS_undefined
        self.combine_alpha_operand2 = self.CO_undefined

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        if self.default:
            dg.add_bool(True)

        else:
            dg.add_bool(False)

            dg.add_string(self.name)
            dg.add_int32(self.sort)
            dg.add_int32(self.priority)

            manager.write_internal_name(dg, self.texcoord_name)

            dg.add_uint8(self.mode)
            dg.add_vec4(self.color)
            dg.add_uint8(self.rgb_scale)
            dg.add_uint8(self.alpha_scale)
            dg.add_bool(self.saved_result)

            if manager.file_version >= (6, 26):
                dg.add_int32(self.tex_view_offset)

            dg.add_uint8(self.combine_rgb_mode)
            dg.add_uint8(self.num_combine_rgb_operands)
            dg.add_uint8(self.combine_rgb_source0)
            dg.add_uint8(self.combine_rgb_operand0)
            dg.add_uint8(self.combine_rgb_source1)
            dg.add_uint8(self.combine_rgb_operand1)
            dg.add_uint8(self.combine_rgb_source2)
            dg.add_uint8(self.combine_rgb_operand2)

            dg.add_uint8(self.combine_alpha_mode)
            dg.add_uint8(self.num_combine_alpha_operands)
            dg.add_uint8(self.combine_alpha_source0)
            dg.add_uint8(self.combine_alpha_operand0)
            dg.add_uint8(self.combine_alpha_source1)
            dg.add_uint8(self.combine_alpha_operand1)
            dg.add_uint8(self.combine_alpha_source2)
            dg.add_uint8(self.combine_alpha_operand2)


TextureStage.default = TextureStage('default')

class Texture(TypedWritableReferenceCount):

    TT_1d_texture = 0
    TT_2d_texture = 1
    TT_3d_texture = 2
    TT_2d_texture_array = 3
    TT_cube_map = 4
    TT_buffer_texture = 4

    T_unsigned_byte = 0
    T_unsigned_short = 1
    T_float = 2
    T_unsigned_int_24_8 = 3
    T_int = 4

    # Only the most important formats supported here
    F_red = 3
    F_alpha = 6
    F_rgb = 7
    F_rgba = 12
    F_luminance = 18
    F_luminance_alpha = 19
    F_rgba16 = 21
    F_rgba32 = 22
    F_r16 = 27
    F_rg16 = 28
    F_rgb16 = 29
    F_srgb = 30
    F_srgb_alpha = 31
    F_r32 = 35
    F_rg32 = 36
    F_rgb32 = 37
    F_rg = 45

    CM_default = 0
    CM_off = 1
    CM_on = 2

    QL_default = 0
    QL_fastest = 1
    QL_normal = 2
    QL_best = 3

    ATS_none = 0
    ATS_down = 1
    ATS_up = 2
    ATS_pad = 3
    ATS_unspecified = 4

    def __init__(self, name=''):
        super().__init__()

        self.name = name
        self.has_rawdata = False
        self.filename = ''
        self.alpha_filename = ''
        self.primary_file_num_channels = 0
        self.alpha_file_channel = 0
        self.texture_type = self.TT_2d_texture
        self.has_read_mipmaps = False

        self.compression = self.CM_default
        self.quality_level = self.QL_default
        self.format = self.F_rgba
        self.num_components = 4
        self.usage_hint = GeomEnums.UH_unspecified
        self.auto_texture_scale = self.ATS_unspecified
        self.orig_file_x_size = 0
        self.orig_file_y_size = 0
        self.has_simple_ram_image = False
        self.simple_x_size = 0
        self.simple_y_size = 0
        self.simple_image_date_generated = 0
        self.simple_ram_image_size = 0
        self.simple_ram_image = bytearray()

        self.x_size = 0
        self.y_size = 1
        self.z_size = 1
        self.pad_x_size = 0
        self.pad_y_size = 0
        self.pad_z_size = 0
        self.num_views = 1
        self.component_type = 0
        self.component_width = 0
        self.ram_image_compression = self.CM_off
        self.ram_images = []

        self.default_sampler = SamplerState()

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # do_write_datagram_header
        dg.add_string(self.name)
        dg.add_string(self.filename)
        dg.add_string(self.alpha_filename)

        dg.add_uint8(self.primary_file_num_channels)
        dg.add_uint8(self.alpha_file_channel)
        dg.add_bool(self.has_rawdata)
        dg.add_uint8(self.texture_type)

        if manager.file_version >= (6, 32):
            dg.add_bool(self.has_read_mipmaps)

        # do_write_datagram_body
        self.default_sampler.write_datagram(manager, dg)

        if manager.file_version >= (6, 1):
            dg.add_uint8(self.compression)

        if manager.file_version >= (6, 16):
            dg.add_uint8(self.quality_level)

        dg.add_uint8(self.format)
        dg.add_uint8(self.num_components)

        if self.texture_type == self.TT_buffer_texture:
            dg.add_uint8(self.usage_hint)

        if manager.file_version >= (6, 28):
            dg.add_uint8(self.auto_texture_scale)

        if manager.file_version >= (6, 18):
            dg.add_uint32(self.orig_file_x_size)
            dg.add_uint32(self.orig_file_y_size)

            dg.add_bool(self.has_simple_ram_image)

            if self.has_simple_ram_image:
                dg.add_uint32(self.simple_x_size)
                dg.add_uint32(self.simple_y_size)
                dg.add_int32(self.simple_image_date_generated)
                dg.add_uint32(self.simple_ram_image_size)
                # dg.append_data(self.simple_ram_image, self.simple_ram_image_size)

        # do_write_datagram_rawdata
        if self.has_rawdata:
            dg.add_uint32(self.x_size)
            dg.add_uint32(self.y_size)
            dg.add_uint32(self.z_size)

            if manager.file_version >= (6, 30):
                dg.add_uint32(self.pad_x_size)
                dg.add_uint32(self.pad_y_size)
                dg.add_uint32(self.pad_z_size)

            if manager.file_version >= (6, 26):
                dg.add_uint32(self.num_views)

            dg.add_uint8(self.component_type)
            dg.add_uint8(self.component_width)

            if manager.file_version >= (6, 1):
                dg.add_uint8(self.ram_image_compression)

            if manager.file_version >= (6, 3):
                dg.add_uint8(len(self.ram_images))


            for ram_image in self.ram_images:
                # assert isinstance(ram_image, RamImage)

                if manager.file_version >= (6, 1):
                    dg.add_uint32(ram_image.page_size)

                dg.add_uint32(ram_image.image_size)
                # dg.append_data(ram_image.image, ram_image.image_size)
