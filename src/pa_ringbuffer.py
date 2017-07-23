"""Python wrapper for PortAudio's ring buffer."""

__version__ = '0.0.0'


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
        _ffi = ffi
        _lib = lib

    return RingBuffer


class _RingBufferBase(object):
    """Wrapper for PortAudio's ring buffer.

    See __init__().

    """

    def __init__(self, elementsize, size):
        """Create an instance of PortAudio's ring buffer.

        http://portaudio.com/docs/v19-doxydocs-dev/pa__ringbuffer_8h.html

        Parameters
        ----------
        elementsize : int
            The size of a single data element in bytes.
        size : int
            The number of elements in the buffer (must be a power of 2).

        """
        self._ptr = self._ffi.new('PaUtilRingBuffer*')
        self._data = self._ffi.new('unsigned char[]', size * elementsize)
        res = self._lib.PaUtil_InitializeRingBuffer(
            self._ptr, elementsize, size, self._data)
        if res != 0:
            assert res == -1
            raise ValueError('size must be a power of 2')

    def flush(self):
        """Reset buffer to empty.

        Should only be called when buffer is NOT being read or written.

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

        Parameters
        ----------
        data : CData pointer or buffer or bytes
            Data to write to the buffer.
        size : int, optional
            The number of elements to be written.

        Returns
        -------
        int
            The number of elements written.

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

        Parameters
        ----------
        size : int, optional
            The number of elements to be read.
            If not specified, all available elements are read.

        Returns
        -------
        buffer
            A new buffer containing the read data.
            Its size may be less than the requested *size*.

        """
        if size < 0:
            size = self.read_available
        data = self._ffi.new('unsigned char[]', size * self.elementsize)
        size = self.readinto(data)
        return self._ffi.buffer(data, size * self.elementsize)

    def readinto(self, data):
        """Read data from the ring buffer into a user-provided buffer.

        Parameters
        ----------
        data : CData pointer or buffer
            The memory where the data should be stored.

        Returns
        -------
        int
            The number of elements read, which may be less than the size
            of *data*.

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

        Parameters
        ----------
        size : int
            The number of elements desired.

        Returns
        -------
        int
            The room available to be written or the given *size*,
            whichever is smaller.
        buffer
            The first buffer.
        buffer
            The second buffer.

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

        Parameters
        ----------
        size : int
            The number of elements to advance.

        Returns
        -------
        int
            The new position.

        """
        return self._lib.PaUtil_AdvanceRingBufferWriteIndex(self._ptr, size)

    def get_read_buffers(self, size):
        """Get buffer(s) from which we can read data.

        Parameters
        ----------
        size : int
            The number of elements desired.

        Returns
        -------
        int
            The number of elements available for reading.
        buffer
            The first buffer.
        buffer
            The second buffer.

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

        Parameters
        ----------
        size : int
            The number of elements to advance.

        Returns
        -------
        int
            The new position.

        """
        return self._lib.PaUtil_AdvanceRingBufferReadIndex(self._ptr, size)

    @property
    def elementsize(self):
        """Element size in bytes."""
        return self._ptr.elementSizeBytes

    def __len__(self):
        """Size of buffer in elements"""
        return self._ptr.bufferSize
