from struct import pack

class Datagram(object):
    """ Reimplementation of Panda's Datagram in Python. """

    __slots__ = ('data', 'stdfloat_format')

    def __init__(self, stdfloat_double=False):
        self.data = bytearray()
        self.stdfloat_format = 'd' if stdfloat_double else 'f'


    def add_bool(self, value):
        self.data.append(int(bool(value)))

    def add_int8(self, value):
        self.data += pack('<b', value)

    def add_int16(self, value):
        self.data += pack('<h', value)

    def add_int32(self, value):
        self.data += pack('<i', value)

    def add_int64(self, value):
        self.data += pack('<q', value)

    def add_uint8(self, value):
        self.data += pack('<B', value)

    def add_uint16(self, value):
        self.data += pack('<H', value)

    def add_uint32(self, value):
        self.data += pack('<I', value)

    def add_uint64(self, value):
        self.data += pack('<Q', value)

    def add_float32(self, value):
        self.data += pack('<f', value)

    def add_float64(self, value):
        self.data += pack('<d', value)

    def add_stdfloat(self, value):
        self.data += pack('<' + self.stdfloat_format, value)

    def add_vec2(self, vec):
        self.data += pack('<' + self.stdfloat_format * 2, *vec)

    def add_vec3(self, vec):
        self.data += pack('<' + self.stdfloat_format * 3, *vec)

    def add_vec4(self, vec):
        self.data += pack('<' + self.stdfloat_format * 4, *vec)

    def add_string(self, value):
        if isinstance(value, str):
            value = value.encode('utf-8')

        assert len(value) <= 65535
        self.data += pack('<H', len(value))
        self.data += value

    def __bytes__(self):
        return pack('<I', len(self.data)) + self.data
