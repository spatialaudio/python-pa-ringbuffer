Python wrapper for PortAudio's ring buffer
==========================================

The ring buffer functionality is typically not included in binary distributions
of PortAudio_, therefore most Python wrappers don't include it, either.

This module can be compiled and used on any Python version where CFFI_ is
available.

The class `pa_ringbuffer.RingBuffer` is designed to be used together with the
sounddevice_ module for non-blocking transfer of data from the main Python
program to an audio callback function which is implemented in C or some other
compiled language.

.. _PortAudio: http://portaudio.com/
.. _sounddevice: http://python-sounddevice.readthedocs.io/
.. _CFFI: http://cffi.readthedocs.io/

Installation
------------

::

    python3 setup.py develop --user

or ::

    python3 -m pip install -e . --user
