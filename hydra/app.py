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
import netifaces
import pyportmidi

from . import client_manager
from . import midi_handler

HYDRA_SERVER_PORT = 5555


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
        socketserver.UDPServer.__init__(self, *args, **kwargs)
        self.allow_reuse_address = True
        self.msg_queue = args[2]


def _choose_gateway(input_domain):
    while True:
        print('Choose a gateway to use: ')
        for idx, possible_gateway in enumerate(input_domain):
            print("%i: %s" % (idx, possible_gateway))
        _input = int(input('>: '))
        if _input in range(len(input_domain)):
            return input_domain[_input]
        else:
            print('Invalid Input. Must be one of the numbers shown.')


if netifaces.AF_INET not in netifaces.gateways():
    print('No network interfaces available')
    sys.exit()

available_gateways = \
    [x for (_, x, _) in netifaces.gateways()[netifaces.AF_INET]]
_gateway = _choose_gateway(available_gateways)
_address = netifaces.ifaddresses(_gateway)[netifaces.AF_INET][0]['addr']
_server_address = (_address, HYDRA_SERVER_PORT)

msg_queue = queue.Queue()
server = MyServer(_server_address, UDPRequestHandler, msg_queue)
