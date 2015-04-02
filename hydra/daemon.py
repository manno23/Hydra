__author__ = 'jm'

import hydra.config
import os.path

class Daemon(object):
    """
The Daemon is created and run as soon as it is instantiated.
A twisted reactor controls the event loop.
    """
    # The core contains the main state of hydra.
    core = Core(listening_interface=listening_interface) # The core contains the main
    rpcserver = RPCServer()                              # This is listening for user
    # events.
    def __init__(self):
        # Ensure only a single instance of the daemon can run
        if os.path.isfile(os.path.join(hydra.config.get_config_dir(), "hydra.pid")):
            pass

