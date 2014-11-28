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
import sys
import queue
import threading
import socketserver
import pyportmidi

from . import client_manager
from . import midi_handler


# ADDRESS = ("127.0.0.1", 5555)
ADDRESS = ("192.168.1.2", 5555)


def run():

    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    pyportmidi.init()
    midi_object = midi_handler.MidiHandler()

    while True:
        try:
            # Get items off the network queue
            try:
                client_manager.handle_message(midi_object,
                                              msg_queue.get(timeout=1/15))
            except queue.Empty:
                pass

            # Get items from the midi buffer
            client_manager.handle_midi(midi_object)

        except KeyboardInterrupt:
            break


def close():
    server.server_close()
    server.shutdown()
    client_manager.close()


class UDPRequestHandler(socketserver.ThreadingMixIn,
                        socketserver.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait((self.request, self.client_address))


class MyServer(socketserver.UDPServer):
    def __init__(self, *args, **kwargs):
        try:
            socketserver.UDPServer.__init__(self, *args, **kwargs)
        except Exception as e:
            print(e)
            print('Target router not connected')
            sys.exit()
        self.allow_reuse_address = True
        self.msg_queue = args[2]

msg_queue = queue.Queue()
server = MyServer(ADDRESS, UDPRequestHandler, msg_queue)
