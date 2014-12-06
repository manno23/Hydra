import sys
import os

from distutils.core import setup
from distutils.extension import Extension


DESCRIPTION = open('README.md').read()
CHANGES = open('CHANGES').read()
TODO = open('TODO').read()

EXTRAS = {}

long_description = DESCRIPTION + CHANGES + TODO

METADATA = {
    'name':             'Hydra',
    'version':          '0.0.1',
    'author':           'manno23',
    'author_email':     'jasonmanning@gmail.com',
    'description':      'Midi controller client control and management',
    'long_description': long_description,
}


if "bdist_msi" in sys.argv:
    # hack the version name to a format msi doesn't have trouble with
    METADATA["version"] = METADATA["version"].replace("pre", "a0")
    METADATA["version"] = METADATA["version"].replace("rc", "b0")
    METADATA["version"] = METADATA["version"].replace("release", "")


PACKAGEDATA = {
    'package_dir': {'hydra': 'hydra'},
    'packages': ['pyportmidi', 'hydra'],
}


PACKAGEDATA.update(METADATA)


if sys.platform == 'win32':
    print("Found Win32 platform")
    EXTENSION = dict(
        ext_modules=[
            Extension("pyportmidi._pyportmidi",
                      [os.path.join("pyportmidi", "_pyportmidi.pyx")],
                      library_dirs=["pyportmidi/windows"],
                      include_dirs=["pyportmidi/includes"],
                      libraries=["portmidi", "winmm"],
                      extra_compile_args=["/DWIN32"])
            # include_dirs=["pyportmidi/porttime"],
            # define_macros = [("_WIN32_", None)])
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
