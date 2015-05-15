 
from .typed_objects import TypedWritableReferenceCount
from .panda_node import PandaNode

class GeomVertexData(TypedWritableReferenceCount):
    bam_type_name = "GeomVertexData"

    UH_client = 0
    UH_stream = 1
    UH_dynamic = 2
    UH_static = 3

    def __init__(self, name=""):
        super().__init__()

        self.name = name
        self.format = None
        self.usage_hint = self.UH_static
        self.arrays = []
        self.transform_table = None
        self.transform_blend_table = None
        self.slider_table = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_string(self.name)

        assert self.format
        # assert isinstance(self.format, GeomVertexFormat) # must be implemented first
        manager.write_pointer(dg, self.format)
        dg.add_uint8(self.usage_hint)
        dg.add_uint16(len(self.arrays))
        for array in self.arrays:
            manager.write_pointer(dg, array)

        manager.write_pointer(dg, self.transform_table)
        manager.write_pointer(dg, self.transform_blend_table)
        manager.write_pointer(dg, self.slider_table)

class Geom(TypedWritableReferenceCount):
    bam_type_name = "Geom"

    SM_uniform = 0
    SM_smooth = 1
    SM_flat_first_vertex = 2
    SM_flat_last_vertex = 3

    PT_none = 0
    PT_polygons = 1
    PT_lines = 2
    PT_points = 3
    PT_patches = 4

    def __init__(self):
        super().__init__()
        self.data = None
        self.primitives = []
        self.primitive_type = self.PT_none
        self.shade_model = self.SM_smooth
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

