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
'''
'''
 HydraServer

    Need to seperate concerns of user interface and midi server.
    Manages phone clients, allowing the sending/receiving of midi messages

    TODO:
    * Add Logging
    * Allow user to configure router or have it done automatically
        - map out the range of possibilites (not plugged in, etc...)
    * Add gui

'''
__version__ = '0.0.1'
__author__ = 'Jason Manning'

import queue
import threading
import socketserver
import pyportmidi

from . import client_manager
from . import midi_handler


HYDRA_SERVER_PORT = 5555


class HydraServer():

    def __init__(self, local_address):
        self.msg_queue = queue.Queue()
        self.server = MyServer(local_address,
                               UDPRequestHandler,
                               self.msg_queue)

    def run(self):

        t = threading.Thread(target=self.server.serve_forever)
        t.daemon = True
        t.start()

        pyportmidi.init()
        midi_object = midi_handler.MidiHandler()

        while True:
            try:
                # Get items off the network queue
                try:
                    client_manager.\
                        handle_message(midi_object,
                                       self.msg_queue.get(timeout=1/15))
                except queue.Empty:
                    pass

                # Get items from the midi buffer
                client_manager.handle_midi(midi_object)

            except KeyboardInterrupt:
                break

    def close(self):
        self.server.server_close()
        self.server.shutdown()
        client_manager.close()


class UDPRequestHandler(socketserver.ThreadingMixIn,
                        socketserver.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait((self.request, self.client_address))


class MyServer(socketserver.UDPServer):
    def __init__(self, *args, **kwargs):
        socketserver.UDPServer.__init__(self, *args, **kwargs)
        self.allow_reuse_address = True
        self.msg_queue = args[2]
