"""
The basic way to run the application is just to call the package
with python. (It must be installed through setup.py because pyportmidi
must be compiled.)

"""

import os
import sys
import importlib

from optparse import OptionParser

from hydra import config


"""
Initialise the reactors
"""
from twisted.internet import reactor

def start_daemon():

    # Check all our dependencies have been met
    # TODO Do we need to check the requirements here? This should be handled in installation
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
    hydra_server = config.get_hydra_instance(config_path)
    hydra_server.run()

    import deluge.common
    deluge.common.setup_translations()

    # Setup the argument parser
    parser = OptionParser(usage="%prog [options] [actions]")
    parser.add_option("-v", "--version", action="callback", callback=version_callback,
                      help="Show program's version number and exit")
    parser.add_option("-p", "--port", dest="port",
                      help="Port daemon will listen on", action="store", type="int")
    parser.add_option("-i", "--interface", dest="listen_interface",
                      help="Interface daemon will listen for bittorrent connections on, \
this should be an IP address", metavar="IFACE",
                      action="store", type="str")
    parser.add_option("-u", "--ui-interface", dest="ui_interface",
                      help="Interface daemon will listen for UI connections on, this should be\
 an IP address", metavar="IFACE", action="store", type="str")
    if not (deluge.common.windows_check() or deluge.common.osx_check()):
        parser.add_option("-d", "--do-not-daemonize", dest="donot",
                          help="Do not daemonize", action="store_true", default=False)
    parser.add_option("-c", "--config", dest="config",
                      help="Set the config location", action="store", type="str")
    parser.add_option("-P", "--pidfile", dest="pidfile",
                      help="Use pidfile to store process id", action="store", type="str")
    if not deluge.common.windows_check():
        parser.add_option("-U", "--user", dest="user",
                          help="User to switch to. Only use it when starting as root", action="store", type="str")
        parser.add_option("-g", "--group", dest="group",
                          help="Group to switch to. Only use it when starting as root", action="store", type="str")
    parser.add_option("-l", "--logfile", dest="logfile",
                      help="Set the logfile location", action="store", type="str")
    parser.add_option("-L", "--loglevel", dest="loglevel",
                      help="Set the log level: none, info, warning, error, critical, debug", action="store", type="str")
    parser.add_option("-q", "--quiet", dest="quiet",
                      help="Sets the log level to 'none', this is the same as `-L none`", action="store_true", default=False)
    parser.add_option("-r", "--rotate-logs",
                      help="Rotate logfiles.", action="store_true", default=False)
    parser.add_option("--profile", dest="profile", action="store_true", default=False,
                      help="Profiles the daemon")

    # Get the options and args from the OptionParser
    (options, args) = parser.parse_args()

    # Setup the logger
    if options.quiet:
        options.loglevel = "none"
    if options.logfile:
        # Try to create the logfile's directory if it doesn't exist
        try:
            os.makedirs(os.path.abspath(os.path.dirname(options.logfile)))
        except OSError, e:
            if e.errno != EEXIST:
                print "There was an error creating the log directory, exiting... (%s)" % e
                sys.exit(1)
    logfile_mode = 'w'
    if options.rotate_logs:
        logfile_mode = 'a'
    setupLogger(level=options.loglevel, filename=options.logfile, filemode=logfile_mode)
    log = getLogger(__name__)

    import deluge.configmanager
    if options.config:
        if not deluge.configmanager.set_config_dir(options.config):
            log.error("There was an error setting the config directory! Exiting...")
            sys.exit(1)

    # Sets the options.logfile to point to the default location
    def open_logfile():
        if not options.logfile:
            options.logfile = deluge.configmanager.get_config_dir("deluged.log")
            file_handler = FileHandler(options.logfile)
            log.addHandler(file_handler)

    # Writes out a pidfile if necessary
    def write_pidfile():
        if options.pidfile:
            open(options.pidfile, "wb").write("%s\n" % os.getpid())

    # If the donot daemonize is set, then we just skip the forking
    if not (deluge.common.windows_check() or deluge.common.osx_check() or options.donot):
        if os.fork():
            # We've forked and this is now the parent process, so die!
            os._exit(0)
        os.setsid()
        # Do second fork
        if os.fork():
            os._exit(0)

    # Write pid file before chuid
    write_pidfile()

    if not deluge.common.windows_check():
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

    def run_daemon(options, args):
        try:
            from deluge.core.daemon import Daemon
            Daemon(options, args)
        except deluge.error.DaemonRunningError, e:
            log.error(e)
            log.error("You cannot run multiple daemons with the same config directory set.")
            log.error("If you believe this is an error, you can force a start by deleting %s.", deluge.configmanager.get_config_dir("deluged.pid"))
            sys.exit(1)
        except Exception, e:
            log.exception(e)
            sys.exit(1)

    if options.profile:
        import cProfile
        profiler = cProfile.Profile()
        profile_output = deluge.configmanager.get_config_dir("deluged.profile")

        # Twisted catches signals to terminate
        def save_profile_stats():
            profiler.dump_stats(profile_output)
            print "Profile stats saved to %s" % profile_output

        from twisted.internet import reactor
        reactor.addSystemEventTrigger("before", "shutdown", save_profile_stats)
        print "Running with profiler..."
        profiler.runcall(run_daemon, options, args)
    else:
        run_daemon(options, args)

def start_gui():
    pass


