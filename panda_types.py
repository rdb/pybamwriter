
class TypedObject(object):
    bam_type_name = "TypedObject"


class TypedWritable(TypedObject):
    bam_type_name = "TypedWritable"

    def write_datagram(self, manager, dg):
        pass

class TypedWritableReferenceCount(TypedWritable):
    bam_type_name = "TypedWritableReferenceCount"


class Material(TypedWritableReferenceCount):
    bam_type_name = "Material"

    def __init__(self, name=""):
        super().__init__(self)
        self.name = str(name)
        self.ambient = None
        self.diffuse = None
        self.specular = None
        self.emission = None
        self.shininess = 0
        self.local = False
        self.twoside = False

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        flags = 0
        if self.ambient:
            flags |= 0x001
        if self.diffuse:
            flags |= 0x002
        if self.specular:
            flags |= 0x004
        if self.emission:
            flags |= 0x008
        if self.local:
            flags |= 0x010
        if self.twoside:
            flags |= 0x020

        dg.add_vec4(self.ambient or (1, 1, 1, 1))
        dg.add_vec4(self.diffuse or (1, 1, 1, 1))
        dg.add_vec4(self.specular or (0, 0, 0, 1))
        dg.add_vec4(self.emission or (0, 0, 0, 1))

        dg.add_stdfloat(self.shininess)
        dg.add_int32(flags)


class RenderState(TypedWritableReferenceCount):
    bam_type_name = "RenderState"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # For now, just write out the value for a state with no attribs
        dg.add_uint16(0)

RenderState.empty = RenderState()


class TransformState(TypedWritableReferenceCount):
    bam_type_name = "TransformState"

    def __init__(self):
        super().__init__(self)
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

            #TODO: check if this is the correct ordering
            for i in (0, 1, 2, 3):
                for j in (0, 1, 2, 3):
                    dg.add_stdfloat(self.mat[i][j])

        else:
            # Identity transform.
            dg.add_uint32(0x00010005)


TransformState.identity = TransformState()


class RenderEffects(TypedWritableReferenceCount):
    bam_type_name = "RenderEffects"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        # For now, just pretend there are 0 render effects.
        dg.add_uint16(0)

RenderEffects.empty = RenderEffects()


class PandaNode(TypedWritableReferenceCount):
    bam_type_name = "PandaNode"

    def __init__(self, name=""):
        super().__init__(self)
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


class GeomVertexData(TypedWritableReferenceCount):
    bam_type_name = "GeomVertexData"

    UH_client = 0
    UH_stream = 1
    UH_dynamic = 2
    UH_static = 3

    def __init__(self, name=""):
        super().__init__(self)

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
        super().__init__(self)
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


class ModelNode(PandaNode):
    bam_type_name = "ModelNode"

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_uint8(0) # PT_none
        dg.add_uint16(0)


class ModelRoot(ModelNode):
    bam_type_name = "ModelRoot"
