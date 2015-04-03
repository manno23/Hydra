__author__ = 'jm'

import os.path
from twisted.internet import reactor
from hydra.rpcserver import RPCServer
from hydra.core import Core

from hydra import log, config, common
logger = log.get_logger()

class Daemon(object):
    """
The Daemon is created and run as soon as it is instantiated.
A twisted reactor controls the event loop.
    """
    core = Core()
    rpc_server = RPCServer()
    pid_file = None

    def __init__(self):
        # Ensure only a single instance of the daemon can run
        if os.path.isfile(config.get_config_dir("deluged.pid")):
            # Get the PID and the port of the supposedly running daemon
            try:
                (pid, port) = open(
                    config.get_config_dir("deluged.pid")
                ).read().strip().split(";")
                pid = int(pid)
                port = int(port)
            except ValueError:
                pid = None
                port = None

            def process_running(pid):
                if common.windows_check():
                    import win32process
                    return pid in win32process.EnumProcesses()
                else:
                    # We can just use os.kill on UNIX to test if the process is running
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        return False
                    else:
                        return True

            if pid is not None and process_running(pid):
                # Ok, so a process is running with this PID, let's make doubly-sure
                # it's a deluged process by trying to open a socket to it's port.
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect(("127.0.0.1", port))
                except socket.error:
                    # Can't connect, so it must not be a deluged process..
                    pass
                else:
                    # This is a deluged!
                    s.close()
                    raise common.DaemonRunningError(
                        "There is a deluge daemon running with this config "
                        "directory!"
                    )
        reactor.addSystemEventTrigger("before", "shutdown", self._shutdown)

    def _shutdown(self, *args, **kwargs):
        """
        Used internally by the Daemon upon a signal to shutdown.
        """
        if self.pid_file is not None:
            try:
                os.remove(config.get_config_dir("deluged.pid"))
            except Exception, e:
                logger.exception(e)
                logger.error("Error removing deluged.pid!")

        log.info("Waiting for components to shutdown..")
