
from .typed_objects import TypedWritableReferenceCount

class Material(TypedWritableReferenceCount):

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

        dg.add_vec4(self.ambient or (1, 1, 1, 1))
        dg.add_vec4(self.diffuse or (1, 1, 1, 1))
        dg.add_vec4(self.specular or (0, 0, 0, 1))
        dg.add_vec4(self.emission or (0, 0, 0, 1))

        dg.add_stdfloat(self.shininess)
        dg.add_int32(flags)