"""Python wrapper for PortAudio's ring buffer.

https://github.com/spatialaudio/python-pa-ringbuffer

"""
__version__ = '0.1.4'


def cdef():
    """Return C declarations needed by CFFI."""
    import platform

    if platform.system() == 'Darwin':
        ring_buffer_size_t = 'int32_t'
    else:
        ring_buffer_size_t = 'long'
    return """
/* Declarations from PortAudio's pa_ringbuffer.h: */
typedef %(ring_buffer_size_t)s ring_buffer_size_t;
typedef struct PaUtilRingBuffer
{
    ring_buffer_size_t  bufferSize;
    volatile ring_buffer_size_t writeIndex;
    volatile ring_buffer_size_t readIndex;
    ring_buffer_size_t bigMask;
    ring_buffer_size_t smallMask;
    ring_buffer_size_t elementSizeBytes;
    char* buffer;
} PaUtilRingBuffer;
ring_buffer_size_t PaUtil_InitializeRingBuffer(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementSizeBytes, ring_buffer_size_t elementCount, void* dataPtr);
void PaUtil_FlushRingBuffer(PaUtilRingBuffer* rbuf);
ring_buffer_size_t PaUtil_GetRingBufferWriteAvailable(const PaUtilRingBuffer* rbuf);
ring_buffer_size_t PaUtil_GetRingBufferReadAvailable(const PaUtilRingBuffer* rbuf);
ring_buffer_size_t PaUtil_WriteRingBuffer(PaUtilRingBuffer* rbuf, const void* data, ring_buffer_size_t elementCount);
ring_buffer_size_t PaUtil_ReadRingBuffer(PaUtilRingBuffer* rbuf, void* data, ring_buffer_size_t elementCount);
ring_buffer_size_t PaUtil_GetRingBufferWriteRegions(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount, void** dataPtr1, ring_buffer_size_t* sizePtr1, void** dataPtr2, ring_buffer_size_t* sizePtr2);
ring_buffer_size_t PaUtil_AdvanceRingBufferWriteIndex(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount);
ring_buffer_size_t PaUtil_GetRingBufferReadRegions(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount, void** dataPtr1, ring_buffer_size_t* sizePtr1, void** dataPtr2, ring_buffer_size_t* sizePtr2);
ring_buffer_size_t PaUtil_AdvanceRingBufferReadIndex(PaUtilRingBuffer* rbuf, ring_buffer_size_t elementCount);
/* End of pa_ringbuffer.h declarations. */
""" % locals()


def init(ffi, lib):
    """Return RingBuffer class using the given CFFI instance."""

    class RingBuffer(_RingBufferBase):
        __doc__ = _RingBufferBase.__doc__
        _ffi = ffi
        _lib = lib

    return RingBuffer


class _RingBufferBase(object):
    """PortAudio's single-reader single-writer lock-free ring buffer.

    C API documentation:
        http://portaudio.com/docs/v19-doxydocs-dev/pa__ringbuffer_8h.html
    Python wrapper:
        https://github.com/spatialaudio/python-pa-ringbuffer

    Instances of this class can be used to transport data between Python
    code and some compiled code running on a different thread.

    This only works when there is a single reader and a single writer
    (i.e. one thread or callback writes to the ring buffer, another
    thread or callback reads from it).

    This ring buffer is *not* appropriate for passing data from one
    Python thread to another Python thread.  For this, the `queue.Queue`
    class from the standard library can be used.

    :param elementsize: The size of a single data element in bytes.
    :type elementsize: int
    :param size: The number of elements in the buffer (must be a power
        of 2). Can be omitted if a pre-allocated buffer is passed.
    :type size: int
    :param buffer: optional pre-allocated buffer to use with RingBuffer.
        Note that if you pass a read-only buffer object, you still get a
        writable RingBuffer; it is your responsibility not to write
        there if the original buffer doesn't expect you to.
    :type buffer: buffer

    """

    def __init__(self, elementsize, size=None, buffer=None):
        self._ptr = self._ffi.new('PaUtilRingBuffer*')
        if buffer is None:
            if size is None:
                raise TypeError(
                    "size is required when buffer parameter is not specified")
            self._data = self._ffi.new('unsigned char[]', size * elementsize)
        elif size is not None:
            raise TypeError('exactly one of {size, buffer} is required')
        else:
            try:
                data = self._ffi.from_buffer(buffer)
            except TypeError:
                data = buffer
            size, rest = divmod(self._ffi.sizeof(data), elementsize)
            if rest:
                raise ValueError('buffer size must be multiple of elementsize')
            self._data = data

        res = self._lib.PaUtil_InitializeRingBuffer(
            self._ptr, elementsize, size, self._data)
        if res != 0:
            assert res == -1
            raise ValueError('size must be a power of 2')

    def flush(self):
        """Reset buffer to empty.

        Should only be called when buffer is **not** being read or
        written.

        """
        self._lib.PaUtil_FlushRingBuffer(self._ptr)

    @property
    def write_available(self):
        """Number of elements available in the ring buffer for writing."""
        return self._lib.PaUtil_GetRingBufferWriteAvailable(self._ptr)

    @property
    def read_available(self):
        """Number of elements available in the ring buffer for reading."""
        return self._lib.PaUtil_GetRingBufferReadAvailable(self._ptr)

    def write(self, data, size=-1):
        """Write data to the ring buffer.

        This advances the write index after writing;
        calling :meth:`advance_write_index` is *not* necessary.

        :param data: Data to write to the buffer.
        :type data: CData pointer or buffer or bytes
        :param size: The number of elements to be written.
        :type size: int, optional
        :returns: The number of elements written.

        """
        try:
            data = self._ffi.from_buffer(data)
        except TypeError:
            pass  # input is not a buffer
        if size < 0:
            size, rest = divmod(self._ffi.sizeof(data), self.elementsize)
            if rest:
                raise ValueError('data size must be multiple of elementsize')
        return self._lib.PaUtil_WriteRingBuffer(self._ptr, data, size)

    def read(self, size=-1):
        """Read data from the ring buffer into a new buffer.

        This advances the read index after reading;
        calling :meth:`advance_read_index` is *not* necessary.

        :param size: The number of elements to be read.
            If not specified, all available elements are read.
        :type size: int, optional
        :returns: A new buffer containing the read data.
            Its size may be less than the requested *size*.

        """
        if size < 0:
            size = self.read_available
        data = self._ffi.new('unsigned char[]', size * self.elementsize)
        size = self.readinto(data)
        return self._ffi.buffer(data, size * self.elementsize)

    def readinto(self, data):
        """Read data from the ring buffer into a user-provided buffer.

        This advances the read index after reading;
        calling :meth:`advance_read_index` is *not* necessary.

        :param data: The memory where the data should be stored.
        :type data: CData pointer or buffer
        :returns: The number of elements read, which may be less than
            the size of *data*.

        """
        try:
            data = self._ffi.from_buffer(data)
        except TypeError:
            pass  # input is not a buffer
        size, rest = divmod(self._ffi.sizeof(data), self.elementsize)
        if rest:
            raise ValueError('data size must be multiple of elementsize')
        return self._lib.PaUtil_ReadRingBuffer(self._ptr, data, size)

    def get_write_buffers(self, size):
        """Get buffer(s) to which we can write data.

        When done writing, use :meth:`advance_write_index` to make the
        written data available for reading.

        :param size: The number of elements desired.
        :type size: int
        :returns:
            * The room available to be written or the given *size*,
              whichever is smaller.
            * The first buffer.
            * The second buffer.
        :rtype: tuple (int, buffer, buffer)

        """
        ptr1 = self._ffi.new('void**')
        ptr2 = self._ffi.new('void**')
        size1 = self._ffi.new('ring_buffer_size_t*')
        size2 = self._ffi.new('ring_buffer_size_t*')
        return (self._lib.PaUtil_GetRingBufferWriteRegions(
                    self._ptr, size, ptr1, size1, ptr2, size2),
                self._ffi.buffer(ptr1[0], size1[0] * self.elementsize),
                self._ffi.buffer(ptr2[0], size2[0] * self.elementsize))

    def advance_write_index(self, size):
        """Advance the write index to the next location to be written.

        :param size: The number of elements to advance.
        :type size: int
        :returns: The new position.

        .. note:: This is only needed when using
            :meth:`get_write_buffers`, the method :meth:`write` takes
            care of this by itself!

        """
        return self._lib.PaUtil_AdvanceRingBufferWriteIndex(self._ptr, size)

    def get_read_buffers(self, size):
        """Get buffer(s) from which we can read data.

        When done reading, use :meth:`advance_read_index` to make the
        memory available for writing again.

        :param size: The number of elements desired.
        :type size: int
        :returns:
            * The number of elements available for reading (which might
              be less than the requested *size*).
            * The first buffer.
            * The second buffer.
        :rtype: tuple (int, buffer, buffer)

        """
        ptr1 = self._ffi.new('void**')
        ptr2 = self._ffi.new('void**')
        size1 = self._ffi.new('ring_buffer_size_t*')
        size2 = self._ffi.new('ring_buffer_size_t*')
        return (self._lib.PaUtil_GetRingBufferReadRegions(
                    self._ptr, size, ptr1, size1, ptr2, size2),
                self._ffi.buffer(ptr1[0], size1[0] * self.elementsize),
                self._ffi.buffer(ptr2[0], size2[0] * self.elementsize))

    def advance_read_index(self, size):
        """Advance the read index to the next location to be read.

        :param size: The number of elements to advance.
        :type size: int
        :returns: The new position.

        .. note:: This is only needed when using
            :meth:`get_read_buffers`, the methods :meth:`read` and
            :meth:`readinto` take care of this by themselves!

        """
        return self._lib.PaUtil_AdvanceRingBufferReadIndex(self._ptr, size)

    @property
    def elementsize(self):
        """Element size in bytes."""
        return self._ptr.elementSizeBytes

    def __len__(self):
        """Size of buffer in elements"""
        return self._ptr.bufferSize
