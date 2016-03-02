from .datagram import Datagram
from .panda_types import TypedWritable, TypedWritableReferenceCount
from collections import deque
from array import array
import sys

BAM_VERSION = (6, 41)

BOC_push = 0
BOC_pop = 1
BOC_adjunct = 2
BOC_remove = 3
BOC_file_data = 4

class InternalName(TypedWritableReferenceCount):
    __slots__ = 'name',

    def __init__(self, name):
        self.name = name

    def write_datagram(self, manager, dg):
        dg.add_string(self.name)


class BamWriter(object):
    """ Reimplementation of Panda's BamWriter in Python. """

    def __init__(self):
        self.target = None

        self.next_object_id = 1
        self.long_object_id = False
        self.next_pta_id = 1
        self.long_pta_id = False
        self.next_type_index = 1

        self.file_version = BAM_VERSION
        self.file_endian = 1 if sys.byteorder == 'little' else 0
        self.file_stdfloat_double = False

        # Keep track of type IDs and object IDs already defined.
        self.types_written = set()
        self.objects_written = set()

        # Map types to type IDs, objects to object IDs, arrays to PTA IDs.
        self.type_map = {}
        self.object_map = {}
        self.pta_map = {}

        # Objects queued up for writing to the stream.
        self.object_queue = deque()

        # Special consideration for type 0.
        self.type_map[None] = 0
        self.types_written.add(0)

    def open_file(self, fn):
        self.target = open(fn, 'wb')
        self.target.write(b'pbj\0\n\r')

        header = Datagram()
        self.write_header(header)
        self.target.write(bytes(header))

    def open_socket(self, host, port):
        import socket
        conn = socket.create_connection((host, port))
        self.target = conn.makefile('wb')

        header = Datagram()
        self.write_header(header)
        self.target.write(bytes(header))

    def close(self):
        self.target.close()

    def write_header(self, dg):
        """ Writes the header datagram.  Called by open_file. """

        dg.add_uint16(self.file_version[0])
        dg.add_uint16(self.file_version[1])
        dg.add_uint8(self.file_endian)
        if self.file_version >= (6, 27):
            dg.add_bool(self.file_stdfloat_double)

    def write_object(self, object):
        """ Writes a single object to the Bam file.

        This implicitly also writes any additional objects
        this object references (if they haven't already been
        written), so that pointers may be fully resolved.

        This may be called repeatedly to write a sequence of
        objects to the Bam file, but typically (especially
        for scene graph files, indicated with the .bam
        extension), only one object is written directly from
        the Bam file: the root of the scene graph.  The
        remaining objects will all be written recursively by
        the first object. """

        self.write_objects((object,))

    def write_objects(self, objects):
        """ Like write_object, but writes more than one object. """

        if len(objects) == 0:
            return

        assert len(self.object_queue) == 0
        self.next_boc = BOC_push

        for object in objects:
            object_id = self.__enqueue_object(object)
            assert object_id != 0
        self.__flush_queue()

        # Finally, write the closing pop.
        dg = Datagram()
        dg.add_uint8(BOC_pop)
        self.target.write(bytes(dg))
        self.target.flush()

    def has_object(self, object):
        """ Returns true if the object has previously been
        written (or at least requested to be written) to the
        bam file, or false if we've never heard of it before.
        """
        return object in self.object_map

    def write_pointer(self, packet, object):
        """ The interface for writing a pointer to another object
        to a Bam file.  This is intended to be called by the
        various objects that write themselves to the Bam
        file, within the write_datagram() method.

        This writes the pointer out in such a way that the
        BamReader will be able to restore the pointer later.
        If the pointer is to an object that has not yet
        itself been written to the Bam file, that object will
        automatically be written. """

        # If the pointer is NULL, we always simply write a zero for an
        # object ID and leave it at that.
        if object is None:
            self.__write_object_id(packet, 0)

        else:
            object_id = self.object_map.get(object)
            if not object_id:
                # We have not written this pointer out yet.  This means we must
                # queue the object definition up for later.
                object_id = self.__enqueue_object(object)

            self.__write_object_id(packet, object_id)

    def write_pta(self, packet, array_data):
        if array_data is None:
            # A zero for the PTA ID indicates a NULL pointer.  This is a
            # special case.
            self.__write_pta_id(packet, 0);

            # Also write a 0 array length so that the bam reader can distinguish
            # previously read arrays from NULL arrays.
            packet.add_uint32(0)

        else:
            assert isinstance(array_data, array)

            pta_id = self.pta_map.get(id(array_data))
            if not pta_id:
                # We have not written this PTA out yet.  Make an ID and do it now.
                pta_id = self.next_pta_id
                self.next_pta_id += 1
                self.pta_map[id(array_data)] = pta_id

                # We trust that the caller used the correct format code.
                packet.add_uint32(len(array_data))
                packet.data += array_data

            self.__write_pta_id(packet, pta_id)

    def write_handle(self, packet, type_handle):
        if type_handle is None:
            packet.add_uint16(0)
            return

        index = self.type_map.get(type_handle)
        if not index:
            # Assign a unique type index to this type.
            index = self.next_type_index
            self.type_map[type_handle] = index
            self.next_type_index += 1

        assert index > 0 and index <= 65535
        packet.add_uint16(index)

        # If this is the first time this type is written out, add type info.
        if index not in self.types_written:
            self.types_written.add(index)

            packet.add_string(type_handle.__name__)

            # Look through all bases (but ignore the base object class)
            bases = [handle for handle in type_handle.__bases__ if handle is not object]

            packet.add_uint8(len(bases))
            for base in bases:
                self.write_handle(packet, base)

    def write_internal_name(self, packet, string):
        """ Convenience method for writing strings where InternalName objects
        are expected. """

        assert isinstance(string, str)

        # We abuse self.object_map to also store a mapping from strings.
        object_id = self.object_map.get(string)
        if not object_id:
            # We have not written this string out yet.  This means we must
            # queue the object definition up for later.
            object_id = self.__enqueue_object(InternalName(string))
            self.object_map[string] = object_id

        self.__write_object_id(packet, object_id)

    def __write_object_id(self, dg, object_id):
        """ Writes the indicated object ID to the datagram. """

        if self.long_object_id:
            dg.add_uint32(object_id)

        else:
            dg.add_uint16(object_id)
            # Once we fill up our uint16, we write all object ID's
            # thereafter with a uint32.
            if object_id == 0xffff:
                self.long_object_id = True

    def __write_pta_id(self, dg, pta_id):
        """ Writes the indicated PTA ID to the datagram. """

        if self.long_pta_id:
            dg.add_uint32(pta_id)

        else:
            dg.add_uint16(pta_id)
            # Once we fill up our uint16, we write all PTA ID's
            # thereafter with a uint32.
            if pta_id == 0xffff:
                self.long_pta_id = True

    def __enqueue_object(self, object):
        """ Assigns an object ID to the object and queues it up
        for later writing to the Bam file.

        The return value is the object ID. """

        assert isinstance(object, TypedWritable)

        object_id = self.object_map.get(object)

        if not object_id:
            # It has not been written before; assign a new object ID.
            object_id = int(self.next_object_id)
            self.object_map[object] = object_id

            self.next_object_id += 1

        self.object_queue.append(object)
        return object_id

    def __flush_queue(self):
        """ Writes all of the objects on the _object_queue to the
        bam stream, until the queue is empty. """

        while self.object_queue:
            object = self.object_queue.popleft()

            dg = Datagram(stdfloat_double=self.file_stdfloat_double)

            if self.file_version >= (6, 21):
                dg.add_uint8(self.next_boc)
                self.next_boc = BOC_adjunct

            object_id = self.object_map[object]

            if object_id not in self.objects_written or object.modified:
                self.write_handle(dg, type(object))
                self.__write_object_id(dg, object_id)

                object.write_datagram(self, dg)
                self.objects_written.add(object_id)
                object.modified = False

            else:
                # If we've already written this object, write it out with
                # type index 0, which is an indicator that the object was
                # previously written and will not be respecified.
                self.write_handle(dg, None)
                self.__write_object_id(dg, object_id)

            # Write out the datagram to the stream.
            self.target.write(bytes(dg))
