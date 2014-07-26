
from Queue import Queue
import SocketServer
from threading import Thread
from hydra import client_manager
from hydra.client_manager import *
from SocketServer import UDPServer
from pygame import midi, time

import unittest


__author__ = 'Jason'

ADDRESS = ('localhost', 5555)
MIDI_TO_BUFFER_DELAY = 10


class MyTestCase(unittest.TestCase):
    def setUp(self):
        """
        We are purely testing the midi conversion and
        manager state change functionality, there is no need
        for the GraphicsManager
        Before all tests we need to create a few fake clients for connecting
        to it.

        Also set up a server to act as the client, this will receive the messages
        sent by the client_manager in response to the midi events
        """
        self.client_manager = ClientManager(None)
        self.midi_simulator = self.client_manager.midi_handler.fake_midi_output_for_testing

        self.msg_queue = Queue()
        self.client_simulator = ClientSimulator(ADDRESS, UDPRequestHandler, self.msg_queue)
        self.t = Thread(target=self.client_simulator.serve_forever)
        self.t.daemon = True
        self.t.start()

    def test_handling_client_connection_message(self):

        # The initial message a client will send is in the request format
        # that the DatagramServer has received,
        # it contains the request as well as it's ID

        #Construct connection msg
        client_id = 1
        data = struct.pack('BB', client_manager.CLIENT_CONNECT, client_id)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection_message = ((data, sock), ADDRESS)
        time.wait(MIDI_TO_BUFFER_DELAY)
        self.client_manager.handle_message(connection_message)

        server_response = self.msg_queue.get(timeout=2)
        response_type = server_response[0][0][0]
        data = struct.unpack('B', response_type)
        self.assertEqual(data, (1,))
        self.assertEqual(len(self.client_manager.client_list), 1)

    def test_midi_kick_event_response(self):
        """
        After initialisation the background is white.
        Connecting returns a confirmation message to the client it does not need to respond to,
        so it is skipped off the message queue and
        """

        #Construct connection msg by client of id:1
        data = struct.pack('BB', client_manager.CLIENT_CONNECT, 1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection_message= ((data, sock), ADDRESS)
        self.client_manager.handle_message(connection_message)

        #Set fountain scene
        self.midi_simulator.note_on(116, 100, 0)
        self.midi_simulator.note_off(116, 100, 0)

        #Push midi message onto signalling a kick drum hit (we arbitrarily have used note 36
        self.midi_simulator.note_on(36, 120, 0)
        self.midi_simulator.note_off(36, 100, 0)
        time.wait(MIDI_TO_BUFFER_DELAY)
        self.client_manager.handle_midi()

        connection_response = self.msg_queue.get(timeout=2) #we can ignore
        scene_update_response = self.msg_queue.get(timeout=2) #we can ignore
        midi_response = self.msg_queue.get(timeout=2)
        data = struct.unpack('BBB', midi_response[0][0])
        self.assertEqual(data, (3, 0, 1))

    def test_activating_a_client(self):
        #Connect clients
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        NUM_CLIENTS = 5
        for client_id in xrange(NUM_CLIENTS):
            data = struct.pack('BB', client_manager.CLIENT_CONNECT, client_id)
            connection_message = ((data, sock), ADDRESS)
            self.client_manager.handle_message(connection_message)
        self.assertEqual(len(self.client_manager.client_list), NUM_CLIENTS)
        self.assertEqual(len(self.client_manager.available_clients), NUM_CLIENTS)
        self.assertEqual(len(self.client_manager.instrument_map.clients), 0)

        # Midi event that signals activating a client
        #(these so far are custom to the user defined scene, as the scene parses this
        # to a generic Client Activation msg

        # Channel 1 is our instrument channel, note 1 signals activating a client
        self.midi_simulator.note_on(121, 100, 1)
        time.wait(MIDI_TO_BUFFER_DELAY)
        self.client_manager.handle_midi()

        self.assertEqual(len(self.client_manager.available_clients), NUM_CLIENTS-1)
        self.assertEqual(len(self.client_manager.instrument_map.clients), 1)

    def test_removing_active_client(self):
        #Client attempts to connect id:2
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = struct.pack('BB', 1, 2)
        connection_message= ((data, sock), ADDRESS)
        self.client_manager.handle_message(connection_message)

        #Make it active for channel 1 using instrument 1
        self.midi_simulator.note_on(121, 100, 1)
        time.wait(MIDI_TO_BUFFER_DELAY)
        self.client_manager.handle_midi()

        #Deactivate the client and send a message to it
        self.midi_simulator.note_on(126, 100, 1)
        time.wait(MIDI_TO_BUFFER_DELAY)
        self.client_manager.handle_midi()
        print 'client -> channel', self.client_manager.instrument_map.clients
        self.assertFalse(self.client_manager.instrument_map.clients.has_key(2))

    def test_instrument_note_definition(self):

        # connect a client
        client_id = 1
        data = struct.pack('BB', client_manager.CLIENT_CONNECT, client_id)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection_message = ((data, sock), ADDRESS)
        self.client_manager.handle_message(connection_message)

        time.wait(MIDI_TO_BUFFER_DELAY)
        server_response = self.msg_queue.get()
        print 'server response connected', server_response


        #assign instrument:2 to channel:1
        self.midi_simulator.note_on(122, 100, 1)

        #begin adding notes to the instrument on channel:1
        self.midi_simulator.note_on(0, 100, 1)
        self.midi_simulator.note_off(0, 100, 1)
        #add notes
        self.midi_simulator.note_on(74, 100, 1)
        self.midi_simulator.note_off(74, 100, 1)
        self.midi_simulator.note_on(52, 100, 1)
        self.midi_simulator.note_off(52, 100, 1)
        self.midi_simulator.note_on(68, 100, 1)
        self.midi_simulator.note_off(68, 100, 1)
        #adding notes stopped
        self.midi_simulator.note_on(0, 100, 1)
        self.midi_simulator.note_off(0, 100, 1)


        time.wait(MIDI_TO_BUFFER_DELAY)
        self.client_manager.handle_midi()

        # notes should be in ascending order
        self.assertEqual(self.client_manager.midi_handler.channel_instruments[1].note_list, [52, 68, 74])

    def tearDown(self):
        self.client_simulator.server_close()
        self.client_simulator.shutdown()
        self.midi_simulator.abort()
        self.midi_simulator.close()
        midi.quit()



class UDPRequestHandler(SocketServer.ThreadingMixIn, SocketServer.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait((self.request, self.client_address))

class ClientSimulator(UDPServer):
    def __init__(self, *args, **kwargs):
        """
        Will throw a socket error here if the address provided is not available.
        @param args:
        @param kwargs:
        @return:
        """
        UDPServer.__init__(self, *args, **kwargs)
        self.allow_reuse_address = True
        self.msg_queue = args[2]


if __name__ == '__main__':
    unittest.main()
