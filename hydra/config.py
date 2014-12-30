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
    print(local_address)
    hydra_server = hydra.HydraServer(local_address)
    return hydra_server


def from_config_file(config_path, hydra_server=None):
    """
    Returns an initialised Hydra Server instance that is ready to be run.

    """
    # read in the configuration
    conf = configparser.ConfigParser()
    with open(config_path, 'r') as config_file:
        conf.read_file(config_file)

    config_dict = {}

    for section in conf.sections():
        config_dict[section] = {}

        for key, val in conf[section].items():
            config_dict[section][key] = val

    return from_config_dict(config_dict)


def create_config(config):
    """
    Guides the user through creating the correct configuration.

    """
    config.add_section('NETWORK')
    config['NETWORK']['local_address'] = _get_address()
    config['NETWORK']['local_port'] = '5555'


def _get_address():
    """
    Returns the address of some selected network gateway interface.

    """
    if netifaces.AF_INET not in netifaces.gateways():
        print('No network interfaces available')
        sys.exit()

    available_gateways = {}
    for i, (_, intf, _) in \
            enumerate(netifaces.gateways()[netifaces.AF_INET]):
        available_gateways[str(i)] = intf
    gateway = handle_console_input(available_gateways)
    address = netifaces.ifaddresses(gateway)[netifaces.AF_INET][0]['addr']

    """
    Why did i have to use the ifaddresses method? instead of just grabbing
    the address from the gateways()[2] tuple?
    this is returning 10.1.1.1, the location of the router.
    The gateways assigned address must be given by the ifaddresses function

    netifaces.gateways()
    - will only return the gateway/interface that is 'active(?)', so if both
    wlan0 and eth0 are plugged in, only one connection is used as a network
    connection , for example browsers will only connect through the single
    'active' gateway.

    """
    return address


def handle_console_input(available_gateways):
    """
    Prompts the user to select a gateway.
    This method handles all possible inputs and guides the user to make
    a correct choice.
    @returns: a string representing the gateway selected

    """
    while True:

        print('\nChoose a gateway by number to use or press \'e\' to exit: ')
        for idx in available_gateways:
            print("    %s: %s" % (idx, available_gateways[idx]))
        key_input = input('    >>: ')

        # Test that is is not nothing
        if key_input is '\n':
            print('Choose a gateway by entering its number.')

        # If given an exit command exit
        elif key_input is ('e' or 'exit' or 'E' or 'Exit'):
            sys.exit()

        # Check that is a valid option
        elif key_input not in available_gateways:
            print('Invalid Input. Must be one of the numbers shown.')

        # Valid choice
        else:
            return available_gateways[key_input]
