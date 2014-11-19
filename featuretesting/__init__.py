#interface to the hydra package
#setup install should produce a package hydra
from daemon import *

'''
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



Methods for creating virtual midi ports: (Also describe default functionality if available)
LINUX: amidi -p <NAME> : creates a virtual midi port if it is not yet already
                        then use -s to send
                                -d to receive
WINDOWS: BeLoop (torrents - or wherever)
OSX:
