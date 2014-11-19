import time
import os
import struct
import socket
import socketserver
import pyportmidi as midi
import queue

from threading import Thread

print('appending Hydra to the path to search for')
import sys
sys.path.append(os.path.join('/home', 'jm', 'code', 'python', 'Hydra'))
print('importing hydra.client_manager')
from hydra.client_manager import (ClientManager, CLIENT_CONNECT)
import unittest


__author__ = 'Jason'

ADDRESS = ('localhost', 5555)
MIDI_TO_BUFFER_DELAY = 0.1


class HandleClientMessageTest(unittest.TestCase):

    def setUp(self):
        """
        We are purely testing the midi conversion and
        manager state change functionality, there is no need
        for the GraphicsManager
        Before all tests we need to create a few fake clients for connecting
        to it.

        Also set up a server to act as the client, this will receive the
        messages sent by the client_manager in response to the midi events
        """
        try:
            self.clientmanager = ClientManager()
        except Exception as e:
            print ('>>>>>> exception being handled')
            print (str(e))
        print ('')
        self.msg_queue = queue.Queue()
        self.client_simulator = \
            ClientSimulator(('localhost', 5556),
                            UDPRequestHandler,
                            self.msg_queue)

        try:
            midi.init()
            self.midi_simulator = midi.Output(4)
            self.midi_simulator.debug = True
        except Exception as e:
            print('we got an exception with getting Midi Output 4!!')
            print (str(e))

        self.t = Thread(target=self.client_simulator.serve_forever)
        self.t.daemon = True
        self.t.start()

    def test_handling_client_connection_message(self):

        # The initial message a client will send is in the request format
        # that the DatagramServer has received,
        # it contains the request as well as it's ID

        # Construct connection msg
        client_id = 1
        data = \
            struct.pack('BB', CLIENT_CONNECT, client_id)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection_message = ((data, sock), ADDRESS)
        self.clientmanager.handle_message(connection_message)

        # TODO Handle the case when
        server_response = self.msg_queue.get(timeout=1)
        response_type = server_response[0][0][0]
        data = struct.unpack('B', response_type)
        self.assertEqual(data, (1,))
        self.assertEqual(len(self.clientmanager.client_list), 1)

    def test_midi_kick_event_response(self):
        """
        After initialisation the background is white.
        Connecting returns a confirmation message to the client it does not
        need to respond to, so it is skipped off the message queue and
        """

        # Construct connection msg by client of id:1
        data = struct.pack('BB', CLIENT_CONNECT, 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection_message = ((data, sock), ADDRESS)
        self.clientmanager.handle_message(connection_message)

        # Set fountain scene
        self.midi_simulator.note_on(116, 100, 0)
        self.midi_simulator.note_off(116, 100, 0)

        # Push midi message onto signalling a kick drum hit (we arbitrarily
        # have used note 36
        self.midi_simulator.note_on(36, 120, 0)
        self.midi_simulator.note_off(36, 100, 0)
        self.clientmanager.handle_midi()

        # Ignore the first 2 message
        self.msg_queue.get(timeout=1)
        self.msg_queue.get(timeout=1)
        midi_response = self.msg_queue.get(timeout=1)
        data = struct.unpack('BBB', midi_response[0][0])
        self.assertEqual(data, (3, 0, 1))

    def test_activating_a_client(self):
        # Connect clients
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        NUM_CLIENTS = 5
        for client_id in range(NUM_CLIENTS):
            data = struct.pack('BB',
                               CLIENT_CONNECT,
                               client_id)
            connection_message = ((data, sock), ADDRESS)

            self.clientmanager.handle_message(connection_message)
        self.assertEqual(len(self.clientmanager.client_list),
                         NUM_CLIENTS)
        self.assertEqual(len(self.clientmanager.available_clients),
                         NUM_CLIENTS)
        self.assertEqual(len(self.clientmanager.instrument_map.clients),
                         0)

        '''
        Midi event that signals activating a client
        (these so far are custom to the user defined scene, as the scene parses
        this to a generic Client Activation msg

        Channel 1 is our instrument channel,
        note 1 signals activating a client '''
        self.midi_simulator.note_on(121, 100, 1)
        self.clientmanager.handle_midi()

        self.assertEqual(len(self.clientmanager.available_clients),
                         NUM_CLIENTS-1)
        self.assertEqual(len(self.clientmanager.instrument_map.clients),
                         1)

    def test_removing_active_client(self):
        # Client attempts to connect id:2
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = struct.pack('BB', 1, 2)
        connection_message = ((data, sock), ADDRESS)
        self.clientmanager.handle_message(connection_message)

        # Make it active for channel 1 using instrument 1
        self.midi_simulator.note_on(121, 100, 1)
        self.clientmanager.handle_midi()

        # Deactivate the client and send a message to it
        self.midi_simulator.note_on(126, 100, 1)
        self.clientmanager.handle_midi()
        print ('client -> channel', self.clientmanager.instrument_map.clients)
        self.assertFalse(2 in self.clientmanager.instrument_map.clients)

    def test_instrument_note_definition(self):

        '''
        The msg_queue is what our client will receive over the network.
        Create a pretend connection-pack and call the client_manager directly,
        skipping the callback from the event loop altogether.
        '''
        client_id = 1
        data = struct.pack('BB',
                           CLIENT_CONNECT,
                           client_id)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection_message = ((data, sock), ADDRESS)
        self.clientmanager.handle_message(connection_message)

        # We are expecting a server connection confirmation messagel
        try:
            server_connection_confirmation = self.msg_queue.get(timeout=1)
        except queue.Empty as e:
            for i in e.__dict__:
                print(i)
            e.__str__ = "A confirmation message was not received"
            raise e

        # assign instrument:2 to channel:1
        self.midi_simulator.note_on(122, 100, 1)

        # begin adding notes to the instrument on channel:1
        self.midi_simulator.note_on(0, 100, 1)
        self.midi_simulator.note_off(0, 100, 1)
        # add notes
        self.midi_simulator.note_on(74, 100, 1)
        self.midi_simulator.note_off(74, 100, 1)
        self.midi_simulator.note_on(52, 100, 1)
        self.midi_simulator.note_off(52, 100, 1)
        self.midi_simulator.note_on(68, 100, 1)
        self.midi_simulator.note_off(68, 100, 1)
        # adding notes stopped
        self.midi_simulator.note_on(0, 100, 1)
        self.midi_simulator.note_off(0, 100, 1)

        self.clientmanager.handle_midi()

        # notes should be in ascending order
        self.assertEqual(self.clientmanager.midi_handler.
                         channel_instruments[1].note_list,
                         [52, 68, 74])

    def tearDown(self):
        self.client_simulator.server_close()
        self.client_simulator.shutdown()
        self.midi_simulator.close()
        midi.quit()


class UDPRequestHandler(socketserver.ThreadingMixIn,
                        socketserver.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait((self.request, self.client_address))


class ClientSimulator(socketserver.UDPServer):
    def __init__(self, *args, **kwargs):
        """
        Will throw a socket error here if the address provided is not available
        @param args:
        @param kwargs:
        @return:
        """
        try:
            socketserver.UDPServer.__init__(self, *args, **kwargs)
        except Exception as e:
            print ('>>>>> Handling UDPServer Exception')
            print (str(e))
            print ('that was the udp server exception!')

        self.allow_reuse_address = True
        self.msg_queue = args[2]


if __name__ == '__main__':
    unittest.main()
