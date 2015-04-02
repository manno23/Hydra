"""
The basic way to run the application is just to call the package
with python. (It must be installed through setup.py because pyportmidi
must be compiled.)

"""

import os
import sys
import configparser
import importlib

from hydra import config


def main():

    # Check all our dependencies have been met
    import_fail = False
    for module in ['netifaces', 'pyportmidi']:
        try:
            importlib.import_module(module)
        except ImportError:
            import_fail = True
            print(('Fatal Error: Unable to find the dependency {}')
                  .format(module))
    if import_fail:
        print("Install all dependencies by running:\
               'pip3 install -r requirements.txt'")
        sys.exit()


    # Create new instance of the server
    hydra_server = config.get_hydra_instance()
    hydra_server.run()


if __name__ == "__main__":
    main()
