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

    CONFIG_FILE_NAME = '.hydra'
    home_dir = os.path.expanduser('~')
    config_path = os.path.join(home_dir, CONFIG_FILE_NAME)
    conf = configparser.ConfigParser()

    # Check if configuration directory exists - this should really
    # not be a problem.
    if not os.path.isdir(home_dir):
        print('Fatal Error: Unable to find a home directory to place\
                configuration file in.')
        sys.exit()

    # If no config file exists, determine settings and create one
    if not os.path.isfile(config_path):

        # We will need to manually configure as well as provide the defaults
        config.create_config(conf)
        with open(config_path, 'w') as config_file:
            conf.write(config_file)

    # Create new instance of the server
    hydra_server = config.from_config_file(config_path)
    hydra_server.run()


if __name__ == "__main__":
    main()
