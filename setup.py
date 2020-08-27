from setuptools import setup

__version__ = 'unknown'

# "import" __version__
for line in open('src/pa_ringbuffer.py'):
    if line.startswith('__version__'):
        exec(line)
        break

LONG_DESCRIPTION = '\n'.join((
    open('README.rst').read(),
    'Version History',
    '---------------',
    '',
    open('NEWS.rst').read(),
))

setup(
    name='pa-ringbuffer',
    version=__version__,
    package_dir={'': 'src'},
    py_modules=['pa_ringbuffer'],
    python_requires='>=2.6',
    author='Matthias Geier',
    author_email='Matthias.Geier@gmail.com',
    description="Python wrapper for PortAudio's ring buffer",
    long_description=LONG_DESCRIPTION,
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
