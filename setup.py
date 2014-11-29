import sys
import os

from distutils.core import setup
from distutils.extension import Extension


DESCRIPTION = open('README.md').read()
CHANGES = open('CHANGES').read()
TODO = open('TODO').read()

EXTRAS = {}

long_description = DESCRIPTION + CHANGES + TODO
# import sys
# if "checkdocs" in sys.argv:
#     print(long_description)


METADATA = {
    'name':             'pyportmidi',
    'version':          '0.0.7',
    'license':          'MIT License',
    'url':              'http://pypi.python.org/pyportmidi/',
    'author':           'John Harrison, Roger B. Dannenberg, Rene Dudfield...',
    'author_email':     'renesd@gmail.com',
    'maintainer':       'Rene Dudfield',
    'maintainer_email': 'renesd@gmail.com',
    'description':      'Python Wrappings for PortMidi #python.',
    'long_description': long_description,
    'classifiers':      [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Cython',
        'Programming Language :: C',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'Topic :: Software Development :: Libraries',
    ],
}


if "bdist_msi" in sys.argv:
    # hack the version name to a format msi doesn't have trouble with
    METADATA["version"] = METADATA["version"].replace("pre", "a0")
    METADATA["version"] = METADATA["version"].replace("rc", "b0")
    METADATA["version"] = METADATA["version"].replace("release", "")


# allow optionally using setuptools for bdist_egg.
using_setuptools = False


PACKAGEDATA = {
    'package_dir': {'pyportmidi': 'pyportmidi'},
    'packages': ['pyportmidi'],
}


PACKAGEDATA.update(METADATA)
PACKAGEDATA.update(EXTRAS)


if sys.platform == 'win32':
    print("Found Win32 platform")
    EXTENSION = dict(
        ext_modules=[
            Extension("PYPortmidi._pyportmidi",
                      [os.path.join("pyportmidi", "_pyportmidi.pyx")],
                      library_dirs=["../Release"],
                      libraries=["portmidi", "winmm"],
                      include_dirs=["../porttime"],
                      # define_macros = [("_WIN32_", None)])
                      extra_compile_args=["/DWIN32"])
        ]
    )
elif sys.platform == 'darwin':
    print("Found darwin (OS X) platform")
    EXTENSION = dict(
        ext_modules=[
            Extension("pyportmidi._pyportmidi",
                      [os.path.join("pyportmidi", "_pyportmidi.c")],
                      library_dirs=["pyportmidi/osx"],
                      include_dirs=["pyportmidi/includes"],
                      libraries=["portmidi"],
                      extra_link_args=["-framework", "CoreFoundation",
                                       "-framework", "CoreMIDI",
                                       "-framework", "CoreAudio"])
        ]
    )
else:
    print("Assuming Linux platform")
    EXTENSION = dict(
        ext_modules=[
            Extension("pyportmidi._pyportmidi",
                      [os.path.join("pyportmidi", "_pyportmidi.c")],
                      library_dirs=["pyportmidi/linux"],
                      libraries=["portmidi", "asound", "pthread"])
        ]
    )

PACKAGEDATA.update(EXTENSION)

setup(**PACKAGEDATA)
