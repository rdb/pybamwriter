
class TypedObject(object):
    __slots__ = ()


class TypedWritable(TypedObject):
    __slots__ = ()

    def write_datagram(self, manager, dg):
        pass


class TypedWritableReferenceCount(TypedWritable):
    __slots__ = ()


class CachedTypedWritableReferenceCount(TypedWritableReferenceCount):
    __slots__ = ()


class CopyOnWriteObject(CachedTypedWritableReferenceCount):
    __slots__ = ()


class NodeCachedReferenceCount(CachedTypedWritableReferenceCount):
    __slots__ = ()
