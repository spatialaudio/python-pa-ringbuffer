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
    py_modules=['pa_ringbuffer'],
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description="Python wrapper for PortAudio's ring buffer",
    long_description=open('README.rst').read(),
    license='MIT',
    keywords='sound audio PortAudio ringbuffer lock-free'.split(),
    url='https://github.com/spatialaudio/python-pa-ringbuffer',
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
