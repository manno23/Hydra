import sys
import os

from distutils.core import setup
from distutils.extension import Extension

EXTRAS = {}

METADATA = {
    'name':             'pyportmidi',
    'version':          '0.0.6',
    'author':           'manno23',
    'author_email':     'jasonmanning@gmail.com',
    'description':      'Python wrapper for the PortMidi libraries',
}


if "bdist_msi" in sys.argv:
    # hack the version name to a format msi doesn't have trouble with
    METADATA["version"] = METADATA["version"].replace("pre", "a0")
    METADATA["version"] = METADATA["version"].replace("rc", "b0")
    METADATA["version"] = METADATA["version"].replace("release", "")


PACKAGEDATA = {
    'packages': ['pyportmidi'],
}


PACKAGEDATA.update(METADATA)


if sys.platform == 'win32':
    print("Found Win32 platform")
    EXTENSION = dict(
        ext_modules=[
            Extension("pyportmidi._pyportmidi",
                      [os.path.join("pyportmidi", "_pyportmidi.c")],
                      libraries=["portmidi", "porttime", "winmm"],
                      library_dirs=[os.path.join("pyportmidi", "win")],
                      include_dirs=[os.path.join("pyportmidi", "includes")],
            )
        ]
   )
elif sys.platform == 'darwin':
    print("Found darwin (OS X) platform")
    EXTENSION = dict(
        ext_modules=[
            Extension("pyportmidi._pyportmidi",
                      [os.path.join("pyportmidi", "_pyportmidi.c")],
                      library_dirs=[os.path.join("pyportmidi", "osx")],
                      include_dirs=[os.path.join("pyportmidi", "includes")],
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
                      library_dirs=["linux"],
                      include_dirs=["includes"],
                      libraries=["portmidi", "asound", "pthread"])
        ]
    )

PACKAGEDATA.update(EXTENSION)

setup(**PACKAGEDATA)
