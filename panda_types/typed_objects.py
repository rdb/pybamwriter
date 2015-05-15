

class TypedObject(object):
    bam_type_name = "TypedObject"

class TypedWritable(TypedObject):
    bam_type_name = "TypedWritable"

    def write_datagram(self, manager, dg):
        pass

class TypedWritableReferenceCount(TypedWritable):
    bam_type_name = "TypedWritableReferenceCount"
