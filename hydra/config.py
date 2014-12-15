import hydra

def from_config_dict(config):
    """
    Initialises the instance with the state defined in the config.

    """
    hydra_server = hydra.ClientManager()

def from_config_file(config_path, hydra_server=None):
    pass
