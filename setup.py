from setuptools import setup

__version__ = 'unknown'

# "import" __version__
for line in open('src/pa_ringbuffer.py'):
    if line.startswith('__version__'):
        exec(line)
        break

setup(
    name='pa-ringbuffer',
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['pa_ringbuffer', '_pa_ringbuffer_build'],
    setup_requires=['CFFI>=1.4.0'],
    cffi_modules=['src/_pa_ringbuffer_build.py:ffibuilder'],
    install_requires=['CFFI>=1'],  # for _cffi_backend
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description="Python wrapper for PortAudio's ring buffer",
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='sound audio PortAudio ringbuffer lock-free'.split(),
    #url='http://python-pa-ringbuffer.readthedocs.io/',
    platforms='any',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
    ],
)
