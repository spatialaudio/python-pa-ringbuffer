"""Build script for the _pa_ringbuffer extension module."""

from cffi import FFI
import platform

if platform.system() == 'Darwin':
    ring_buffer_size_t = 'int32_t'
else:
    ring_buffer_size_t = 'long'

RINGBUFFER_DECLARATIONS = """
/* Excerpt from PortAudio's pa_ringbuffer.h: */

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

ffibuilder = FFI()
ffibuilder.cdef(RINGBUFFER_DECLARATIONS)
ffibuilder.set_source(
    '_pa_ringbuffer',
    RINGBUFFER_DECLARATIONS,
    sources=['portaudio/src/common/pa_ringbuffer.c'],
)

if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
