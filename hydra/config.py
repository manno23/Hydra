import sys
import hydra
import netifaces
import configparser


def from_config_dict(config):
    """
    Initialises the instance with the state defined in the config.

    """
    local_address = (
        config['NETWORK']['local_address'],
        int(config['NETWORK']['local_port'])
        )
    hydra_server = hydra.HydraServer(local_address)
    return hydra_server


def from_config_file(config_path, hydra_server=None):
    """
    Returns an initialised Hydra Server instance that is ready to be run.

    """
    # read in the configuration
    config = configparser.ConfigParser()
    config.read_file(config_path)

    config_dict = {}

    for section in config.sections():
        config_dict[section] = {}

        for key, val in config[section]:
            config_dict[section][key] = val

    return from_config_dict(config_dict)


def create_config(config):
    """
    Guides the user through creating the correct configuration.

    """
    config['NETWORK']['local_address'] = _get_address()
    config['NETWORK']['local_port'] = 5555


def _get_address():
    if netifaces.AF_INET not in netifaces.gateways():
        print('No network interfaces available')
        sys.exit()

    available_gateways = \
        [x for (_, x, _) in netifaces.gateways()[netifaces.AF_INET]]

    while True:
        print('Choose a gateway to use: ')
        for idx, possible_gateway in enumerate(available_gateways):
            print("%i: %s" % (idx, possible_gateway))
        input = int(input('>: '))
        if input in range(len(available_gateways)):
            gateway = available_gateways[input]
        else:
            print('Invalid Input. Must be one of the numbers shown.')

    address = netifaces.ifaddresses(gateway)[netifaces.AF_INET][0]['addr']
    return address
