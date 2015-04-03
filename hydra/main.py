"""
Gives the two main entrance points, for either the daemon by itself,
or create a Gtk gui that connects with a daemon.

"""
import os
import sys
import importlib
from optparse import OptionParser
from hydra import common, config, log


def start_daemon():
    # Check all our dependencies have been met
    # TODO Do we need to check the requirements here? This should be handled in installation
    import_fail = False
    for module in ['netifaces', 'pyportmidi']:
        try:
            importlib.import_module(module)
        except ImportError:
            import_fail = True
            print('Fatal Error: Unable to find the dependency {}'
                  .format(module))
    if import_fail:
        print("Install all dependencies by running 'pip install -r requirements.txt'")
        sys.exit()

    # Setup the argument parser
    parser = OptionParser(usage="%prog [options] [actions]")
    parser.add_option("-v", "--version", action="callback", callback=common.get_version,
                      help="Show program's version number and exit")
    parser.add_option("-p", "--port", dest="port",
                      help="Port daemon will listen on", action="store", type="int")
    parser.add_option("-c", "--config", dest="config",
                      help="The path of the config file", action="store", type="str")
    parser.add_option("-l", "--logfile", dest="logfile",
                      help="Set the logfile location", action="store", type="str")
    parser.add_option("-P", "--pidfile", dest="pidfile",
                      help="Path of the pidfile, the pidfile stores process id",
                      action="store", type="str")
    if not common.windows_check():
        parser.add_option("-U", "--user", dest="user",
                          help="User to switch to. Only use it when starting as root",
                          action="store", type="str")
        parser.add_option("-g", "--group", dest="group",
                          help="Group to switch to. Only use it when starting as root",
                          action="store", type="str")

    # Get the options and args from the OptionParser
    (options, args) = parser.parse_args()

    # Setup the logger
    log.initialise(options)

    if options.config:
        try:
            config.set_config_dir(options.config)
        except Exception:
            log.error("There was an error setting the config directory! Exiting...")
        sys.exit(1)


    # Sets the options.logfile to point to the default location
    def open_logfile():
        if not options.logfile:
            options.logfile = config.get_config_dir("hydrad.log")
            file_handler = log.FileHandler(options.logfile)
            log.addHandler(file_handler)
        else:
            # TODO Check if this is a current file
            pass


    # Writes out a pidfile if necessary
    def write_pidfile():
        if options.pidfile:
            open(options.pidfile, "wb").write("%s\n" % os.getpid())


    write_pidfile()

    # For running the daemon with different user or group permissions
    if not common.windows_check():
        if options.user:
            if not options.user.isdigit():
                import pwd

                options.user = pwd.getpwnam(options.user)[2]
            os.setuid(options.user)
        if options.group:
            if not options.group.isdigit():
                import grp

                options.group = grp.getgrnam(options.group)[2]
            os.setuid(options.group)

    open_logfile()
    try:
        from hydra.daemon import Daemon

        Daemon(options, args)
    except common.DaemonRunningError, e:
        log.error(e)
        log.error("You cannot run multiple daemons with the same config directory set.")
        log.error(
            "If you believe this is an error you can force a restart by deleting %s.",
            os.path.join(config.get_config_dir(), "deluged.pid"))
        sys.exit(1)
    except Exception, e:
        log.exception(e)
        sys.exit(1)


    def start_gui():
        pass
