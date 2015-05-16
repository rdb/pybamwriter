

class TypedObject(object):
    pass


class TypedWritable(TypedObject):

    def write_datagram(self, manager, dg):
        pass


class TypedWritableReferenceCount(TypedWritable):
    pass


class CachedTypedWritableReferenceCount(TypedWritableReferenceCount):
    pass


class CopyOnWriteObject(CachedTypedWritableReferenceCount):
    pass


class NodeCachedReferenceCount(CachedTypedWritableReferenceCount):
    pass
