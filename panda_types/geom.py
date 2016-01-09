
from .typed_objects import CopyOnWriteObject, TypedWritableReferenceCount
from .panda_node import PandaNode
from .render_states import RenderState

from collections import namedtuple

class GeomEnums:
    UH_client = 0
    UH_stream = 1
    UH_dynamic = 2
    UH_static = 3
    UH_unspecified = 4

    NT_uint8 = 0
    NT_uint16 = 1
    NT_uint32 = 2
    NT_packed_dcba = 3,
    NT_packed_dabc = 4,
    NT_float32 = 5
    NT_float64 = 6
    NT_stdfloat = 7
    NT_int8 = 8
    NT_int16 = 9
    NT_int32 = 10
    NT_packed_ufloat = 11

    SM_uniform = 0
    SM_smooth = 1
    SM_flat_first_vertex = 2
    SM_flat_last_vertex = 3

    C_other = 0
    C_point = 1
    C_clip_point = 2
    C_vector = 3
    C_texcoord = 4
    C_color = 5
    C_index = 6
    C_morph_delta = 7
    C_matrix = 8
    C_normal = 9



GeomVertexColumn = namedtuple("GeomVertexColumn", ("name", "num_components", 
    "numeric_type", "contents", "start", "column_alignment"))


class GeomVertexArrayFormat(TypedWritableReferenceCount):

    def __init__(self):
        super().__init__()

        self.stride = 0
        self.total_bytes = 0
        self.pad_to = 0
        self.divisor = 0

        self.columns = []

    def add_column(self, *args, **kwargs):
        self.columns.append(GeomVertexColumn(*args, **kwargs))

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(self.stride)
        dg.add_uint16(self.total_bytes)
        dg.add_uint8(self.pad_to)

        if manager.file_version >= (6, 37):
            dg.add_uint16(self.divisor)

        dg.add_uint16(len(self.columns))
        for column in self.columns:
            manager.write_internal_name(dg, column.name)
            dg.add_uint8(column.num_components)
            dg.add_uint8(column.numeric_type)
            dg.add_uint8(column.contents)
            dg.add_uint16(column.start)

            if manager.file_version >= (6, 29):
                dg.add_uint8(column.column_alignment)


class GeomVertexArrayData(CopyOnWriteObject):

    def __init__(self, array_format, usage_hint):
        super().__init__()

        self.array_format = array_format
        self.usage_hint = usage_hint
        self.buffer = bytearray()

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        assert isinstance(self.array_format, GeomVertexArrayFormat)

        manager.write_pointer(dg, self.array_format)
        dg.add_uint8(self.usage_hint)
        dg.add_uint32(len(self.buffer))
        dg.data += self.buffer


class GeomVertexFormat(TypedWritableReferenceCount):

    def __init__(self, *args):
        super().__init__()

        self.arrays = list(args)

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        #TODO: vertex animation spec
        dg.add_uint8(0)
        dg.add_uint16(0)
        dg.add_bool(False)

        dg.add_uint16(len(self.arrays))
        for array in self.arrays:
            assert isinstance(array, GeomVertexArrayFormat)
            manager.write_pointer(dg, array)

class GeomVertexData(CopyOnWriteObject):

    def __init__(self, name, vertex_format, usage_hint):
        super().__init__()

        self.name = name
        self.format = vertex_format
        self.usage_hint = usage_hint
        self.arrays = []
        self.transform_table = None
        self.transform_blend_table = None
        self.slider_table = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_string(self.name)

        assert isinstance(self.format, GeomVertexFormat)
        manager.write_pointer(dg, self.format)
        dg.add_uint8(self.usage_hint)
        dg.add_uint16(len(self.arrays))
        for array in self.arrays:
            manager.write_pointer(dg, array)

        manager.write_pointer(dg, self.transform_table)
        manager.write_pointer(dg, self.transform_blend_table)
        manager.write_pointer(dg, self.slider_table)


class Geom(CopyOnWriteObject):

    PT_none = 0
    PT_polygons = 1
    PT_lines = 2
    PT_points = 3
    PT_patches = 4

    def __init__(self, vertex_data):
        super().__init__()
        self.data = vertex_data
        self.primitives = []
        self.primitive_type = self.PT_none
        self.shade_model = GeomEnums.SM_smooth
        self.bounds_type = 0

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        assert self.data
        assert isinstance(self.data, GeomVertexData)
        manager.write_pointer(dg, self.data)

        dg.add_uint16(len(self.primitives))
        for primitive in self.primitives:
            manager.write_pointer(dg, primitive)

        dg.add_uint8(self.primitive_type)
        dg.add_uint8(self.shade_model)
        dg.add_uint16(0) # reserved

        if manager.file_version >= (6, 19):
            dg.add_uint8(self.bounds_type)


class GeomPrimitive(CopyOnWriteObject):

    def __init__(self, usage_hint):
        super().__init__()
        self.shade_model = GeomEnums.SM_smooth
        self.first_vertex = 0
        self.num_vertices = 0
        self.index_type = GeomEnums.NT_uint16
        self.usage_hint = usage_hint
        self.vertices = None
        self.ends = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint8(self.shade_model)
        dg.add_int32(self.first_vertex)
        dg.add_int32(self.num_vertices)
        dg.add_uint8(self.index_type)
        dg.add_uint8(self.usage_hint)

        assert self.vertices is None or isinstance(self.vertices, GeomVertexArrayData)
        manager.write_pointer(dg, self.vertices)
        manager.write_pta(dg, self.ends)


class GeomPoints(GeomPrimitive):
    pass


class GeomLines(GeomPrimitive):
    pass


class GeomLinestrips(GeomPrimitive):
    pass


class GeomTriangles(GeomPrimitive):
    pass


class GeomTristrips(GeomPrimitive):
    pass


class GeomTrifans(GeomPrimitive):
    pass


class GeomTrifans(GeomPrimitive):
    pass


class GeomPatches(GeomPrimitive):

    def __init__(self, num_vertices_per_patch, usage_hint):
        super().__init__(usage_hint)

        self.num_vertices_per_patch = num_vertices_per_patch

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(self.num_vertices_per_patch)


class GeomNode(PandaNode):

    def __init__(self, name=""):
        super().__init__(name)

        # Geoms should be a list of tuples, in the format (Geom, RenderState)
        self.geoms = []

    def add_geom(self, geom, state=RenderState.empty):
        self.geoms.append((geom, state))

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint16(len(self.geoms))

        for geom, render_state in self.geoms:
            assert isinstance(geom, Geom)
            assert isinstance(render_state, RenderState)
            manager.write_pointer(dg, geom)
            manager.write_pointer(dg, render_state)

