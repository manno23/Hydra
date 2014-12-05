"""
The basic way to run the application is just to call the package
with python.

"""

import os
import argparse
import importlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', '--config',
        metavar='path_to_config_dir',
        default="config",
        help="Directory containing our hydra.conf")

    args = parser.parse_args()

    # Check all our dependencies have been met
    import_fail = False
    for module in ['requests']:
        try:
            importlib.import_module(module)
        except ImportError:
            import_fail = True
            print(('Fatal Error: Unable to find the dependency {}')
                  .format(module))
    if import_fail:
        print("Install all dependencies by running: "
              "pip3 install -r requirement.txt")
        exit()

    # Check if configuration directory exists
    config_dir = os.path.join(os.getcwd(), args.config)
    if not os.path.isdir(config_dir):
        print(('Fatal Error: Unable to findspecified configuration '
              'directory {}').format(config_dir))
        exit()
    config_path = os.path.join(config_dir, 'hydra.conf')

    # If no config file exists, create a default
    if not os.path.isfile(config_path):
        try:
            with open(config_path, 'w') as conf:
                conf.write("This is the new config file for Hydra!")
        except IOError:
            print(('Fatal Error: Unable to create new config file '
                  'to the path {}').format(config_path))
            exit()

    # Create new instance of the server
    hydra_server = config.from_config_file(config_path)



if __name__ == "__main__":
    main()
