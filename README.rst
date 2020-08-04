Python wrapper for PortAudio's ring buffer
==========================================

The `ring buffer functionality`_ is typically not included in binary
distributions of PortAudio_, therefore most Python wrappers don't include it,
either.

The ``pa_ringbuffer`` module provides only a Python wrapper, the actual
PortAudio ring buffer code has to be compiled separately, see Usage_.
It can be used on any Python version where CFFI_ is available.

This module is designed to be used together with the sounddevice_ module (it
might work with other modules, too) for non-blocking transfer of data between
the main Python program and an audio callback function which is implemented in C
or some other compiled language.

.. _PortAudio: http://portaudio.com/
.. _ring buffer functionality: http://portaudio.com/docs/v19-doxydocs-dev/
                               pa__ringbuffer_8h.html
.. _sounddevice: http://python-sounddevice.readthedocs.io/
.. _CFFI: http://cffi.readthedocs.io/

Usage
-----

This module is not meant to be used on its own, it is only useful in cooperation
with another Python module using CFFI.
For an example, have a look at https://github.com/spatialaudio/python-rtmixer.

You can get the Python code from PyPI_, for example in your ``setup.py`` file
(in the following example, your module would be called ``mycffimodule``):

.. code:: python

    from setuptools import setup
    
    setup(
        name=...,
        version=...,
        author=...,
        ...,
        cffi_modules=['mycffimodule_build.py:ffibuilder'],
        setup_requires=['CFFI', 'pa_ringbuffer'],
        install_requires=['pa_ringbuffer'],
        ...,
    )

.. _PyPI: https://pypi.python.org/pypi/pa-ringbuffer

Alternatively, you can just copy the file ``src/pa_ringbuffer.py`` to your own
source directory and import it from there.

You can build your own CFFI module like described in
http://cffi.readthedocs.io/en/latest/cdef.html, just adding a few more bits to
your ``mycffimodule_build.py``:

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
use something like this in your own module to get access to the ``RingBuffer``
class:

.. code:: python

    import pa_ringbuffer
    from _mycffimodule import ffi, lib

    RingBuffer = pa_ringbuffer.init(ffi, lib)

API Reference
-------------

There are only two functions:

``pa_ringbuffer.cdef()``
^^^^^^^^^^^^^^^^^^^^^^^^

This function returns a string containing C declarations from the file
``pa_ringbuffer.h``, which can be used as argument to CFFI's `cdef()`_ function
(see Usage_ above).  Note that the returned declarations are slightly different
when called on a macOS/Darwin system.

.. _cdef(): http://cffi.readthedocs.io/en/latest/
            cdef.html#ffi-ffibuilder-cdef-declaring-types-and-functions

``pa_ringbuffer.init(ffi, lib)``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This function returns the ``RingBuffer`` class which is associated with the CFFI
instance given by ``ffi`` and ``lib``.

Creating the Documentation
--------------------------

The documentation of the ``RingBuffer`` class is not available separately.
If you are using Sphinx_, you can seamlessly include the documentation of the
``RingBuffer`` class with your own documentation.
An example for this can be found at
https://github.com/spatialaudio/python-rtmixer, the generated documentation is
available at http://python-rtmixer.readthedocs.io/#rtmixer.RingBuffer.

You'll need to have the autodoc_ extension activated in your ``conf.py``:

.. code:: python

    extensions = [
        ...,
        'sphinx.ext.autodoc',
        ...,
    ]

And somewhere within your module documentation, you should add this:

.. code:: rst

    .. autoclass:: RingBuffer
       :inherited-members:

Before that, you might have to use the currentmodule_ directive to select your
own module.  Using automodule_ should also do.

If you want to use Sphinx's nitpicky_ setting,
you'll have to add a few things to ``nitpick_ignore``:

.. code:: python

    nitpicky = True
    nitpick_ignore = [
        ('py:class', 'optional'),
        ('py:class', 'buffer'),
        ('py:class', 'CData pointer'),
    ]

.. _Sphinx: http://www.sphinx-doc.org/
.. _autodoc: http://www.sphinx-doc.org/ext/autodoc.html
.. _currentmodule: http://www.sphinx-doc.org/domains.html
                   #directive-py:currentmodule
.. _automodule: http://www.sphinx-doc.org/ext/autodoc.html#directive-automodule
.. _nitpicky: https://www.sphinx-doc.org/en/master/
    usage/configuration.html#confval-nitpicky
