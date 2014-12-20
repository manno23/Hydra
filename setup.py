import sys

from distutils.core import setup


DESCRIPTION = open('README.md').read()
CHANGES = open('CHANGES').read()
TODO = open('TODO').read()

EXTRAS = {}

long_description = DESCRIPTION + CHANGES + TODO

METADATA = {
    'name':             'hydra',
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
    'packages': ['hydra'],
}
PACKAGEDATA.update(METADATA)


setup(**PACKAGEDATA)
