Python wrapper for PortAudio's ring buffer
==========================================

The ring buffer functionality is typically not included in binary distributions
of PortAudio_, therefore most Python wrappers don't include it, either.

This module can be compiled and used on any Python version where CFFI_ is
available.

This module is designed to be used together with the sounddevice_ module
(it might work with other modules, too) for non-blocking transfer of data from
the main Python program to an audio callback function which is implemented in C
or some other compiled language.

.. _PortAudio: http://portaudio.com/
.. _sounddevice: http://python-sounddevice.readthedocs.io/
.. _CFFI: http://cffi.readthedocs.io/

Installation
------------

Use this if you want to install it locally in a development environment::

    python3 setup.py develop --user

or ::

    python3 -m pip install -e . --user

Usage
-----

This module is not meant to be used on its own, it is only useful in cooperation
with another Python module using CFFI.

You can get the Python code from PyPI (Note: not yet available!),
for example in your ``setup.py`` file:

.. code:: python

    from setuptools import setup
    
    setup(
        name=...,
        version=...,
        author=...,
        ...,
        setup_requires=['CFFI', 'pa_ringbuffer'],
        install_requires=['pa_ringbuffer'],
        ...,
    )

Alternatively, you can just copy the file ``src/pa_ringbuffer.py`` to your own
source directory and import it from there.

You can build your own CFFI module like described in
http://cffi.readthedocs.io/en/latest/cdef.html, just adding a few more bits:

.. code:: python

    from cffi import FFI
    import pa_ringbuffer
    
    ffibuilder = FFI()
    ffibuilder.cdef(pa_ringbuffer.cdef())
    ffibuilder.cdef("""
    
    /* my own declarations */
    
    """)
    ffibuilder.set_source(
        '_mycffimodule',
        '/* my implementation */',
        sources=['portaudio/src/common/pa_ringbuffer.c'],
    )
    
    if __name__ == '__main__':
        ffibuilder.compile(verbose=True)

Note that the following files must be available to the compiler:

* https://app.assembla.com/spaces/portaudio/git/source/master/src/common/pa_ringbuffer.c
* https://app.assembla.com/spaces/portaudio/git/source/master/src/common/pa_ringbuffer.h
* https://app.assembla.com/spaces/portaudio/git/source/master/src/common/pa_memorybarrier.h

For your own C code, you might need some definitions from the main PortAudio
header:

* https://app.assembla.com/spaces/portaudio/git/source/master/include/portaudio.h

Once you have compiled your extension module (with the help of CFFI), you can
use something like this to get access to the ``RingBuffer`` class:

.. code:: python

    import pa_ringbuffer
    from _mycffimodule import ffi, lib

    RingBuffer = pa_ringbuffer.init(ffi, lib)
