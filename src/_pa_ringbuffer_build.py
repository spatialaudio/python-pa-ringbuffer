"""Build script for the _pa_ringbuffer extension module."""

from cffi import FFI
import platform

if platform.system() == 'Darwin':
    ring_buffer_size_t = 'int32_t'
else:
    ring_buffer_size_t = 'long'

_TYPES = """
/* Types from PortAudio's pa_ringbuffer.h: */
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
/* End of pa_ringbuffer.h types. */
""" % locals()

_FUNCTION_DECLARATIONS = """
/* Function declarations from PortAudio's pa_ringbuffer.h: */
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
/* End of pa_ringbuffer.h functions. */
"""

_FUNCTION_POINTER_DECLARATIONS = """
ring_buffer_size_t (*PaUtil_InitializeRingBuffer)(PaUtilRingBuffer*, ring_buffer_size_t, ring_buffer_size_t, void*);
void (*PaUtil_FlushRingBuffer)(PaUtilRingBuffer*);
ring_buffer_size_t (*PaUtil_GetRingBufferWriteAvailable)(const PaUtilRingBuffer*);
ring_buffer_size_t (*PaUtil_GetRingBufferReadAvailable)(const PaUtilRingBuffer*);
ring_buffer_size_t (*PaUtil_WriteRingBuffer)(PaUtilRingBuffer*, const void*, ring_buffer_size_t);
ring_buffer_size_t (*PaUtil_ReadRingBuffer)(PaUtilRingBuffer*, void*, ring_buffer_size_t);
ring_buffer_size_t (*PaUtil_GetRingBufferWriteRegions)(PaUtilRingBuffer*, ring_buffer_size_t, void**, ring_buffer_size_t*, void**, ring_buffer_size_t*);
ring_buffer_size_t (*PaUtil_AdvanceRingBufferWriteIndex)(PaUtilRingBuffer*, ring_buffer_size_t);
ring_buffer_size_t (*PaUtil_GetRingBufferReadRegions)(PaUtilRingBuffer*, ring_buffer_size_t, void**, ring_buffer_size_t*, void**, ring_buffer_size_t*);
ring_buffer_size_t (*PaUtil_AdvanceRingBufferReadIndex)(PaUtilRingBuffer*, ring_buffer_size_t);
"""

CDEF = _TYPES + _FUNCTION_POINTER_DECLARATIONS

SOURCE = _TYPES + '\n'.join(
    'static ' + line for line in _FUNCTION_POINTER_DECLARATIONS.strip().split('\n')
)

ffibuilder = FFI()
ffibuilder.cdef(_TYPES + _FUNCTION_DECLARATIONS)
ffibuilder.set_source(
    '_pa_ringbuffer',
    _TYPES + _FUNCTION_DECLARATIONS,
    sources=['portaudio/src/common/pa_ringbuffer.c'],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
