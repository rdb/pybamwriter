
from .typed_objects import TypedWritableReferenceCount

class Material(TypedWritableReferenceCount):

    """ To use metalness workflow, set metallic to something other than None """

    __slots__ = ('name', 'ambient', 'diffuse', 'specular', 'emission', 'shininess',
                 'local', 'twoside', 'attrib_lock', 'roughness', 'metallic',
                 'base_color', 'refractive_index')

    def __init__(self, name=""):
        super().__init__()
        self.name = str(name)
        self.ambient = None
        self.diffuse = None
        self.specular = None
        self.emission = None
        self.shininess = 0
        self.local = False
        self.twoside = False
        self.attrib_lock = False
        self.roughness = None
        self.metallic = None
        self.base_color = None
        self.refractive_index = None

    def write_datagram(self, manager, dg):
        super().write_datagram(manager, dg)

        dg.add_string(self.name)

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
        if self.attrib_lock:
            flags |= 0x040

        if manager.file_version >= (6, 39):
            if self.roughness is not None:
                flags |= 0x080
            if self.metallic is not None:
                flags |= 0x100
            if self.base_color is not None:
                flags |= 0x200
            if self.refractive_index is not None:
                flags |= 0x400

            dg.add_int32(flags)
            if self.metallic is not None:
                # Metalness workflow.
                dg.add_vec4(self.base_color or (1, 1, 1, 1))
                dg.add_stdfloat(self.metallic)
            else:
                dg.add_vec4(self.ambient or (1, 1, 1, 1))
                dg.add_vec4(self.diffuse or (1, 1, 1, 1))
                dg.add_vec4(self.specular or (0, 0, 0, 1))

            dg.add_vec4(self.emission or (0, 0, 0, 1))

            if self.roughness is not None:
                dg.add_stdfloat(self.roughness)
            else:
                dg.add_stdfloat(self.shininess)

            dg.add_stdfloat(self.refractive_index or 1)

        else:
            dg.add_vec4(self.ambient or (1, 1, 1, 1))
            dg.add_vec4(self.diffuse or (1, 1, 1, 1))
            dg.add_vec4(self.specular or (0, 0, 0, 1))
            dg.add_vec4(self.emission or (0, 0, 0, 1))

            dg.add_stdfloat(self.shininess)
            dg.add_int32(flags)
