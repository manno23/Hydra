'''
interface to the hydra package
setup install should produce a package hydra
hydra will include
 - the hydra daemon => run(), non blocking allows other functions to be called

 - socket server -> receiving/sending
 - event_loop -> checks server buffer
              -> check midi buffer
              -> send messages
              -> rudimentary keyboard event detection
 - config files
 - logging

 - the user interface => interface() -> blocking(checks to see if running)

Methods for creating virtual midi ports: (Also describe default functionality
if available)

LINUX: amidi -p <NAME> : creates a virtual midi port if it is not yet already
                        then use -s to send
                                -d to receive
        sudo modprobe snd-virmidi: gives you virtual midi ports to play with!!

WINDOWS: BeLoop (torrents - or wherever)
OSX:

 HydraServer

    Need to seperate concerns of user interface and midi server.
    Manages phone clients, allowing the sending/receiving of midi messages

    TODO:
    * Add Logging
    * Allow user to configure router or have it done automatically
        - map out the range of possibilites (not plugged in, etc...)
    * Add gui
No need to baby user, can create wiki with how to setup virtual
ports and direct them to the log files that are available to them
It will not have debug level log, only above.

'''

__version__ = '0.0.1'
__author__ = 'Jason Manning'
