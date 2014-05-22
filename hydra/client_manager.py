import socket
import struct
from collections import namedtuple
from hydra.midihandler import MidiHandler


client = namedtuple('client', ['id', 'address'])

# Midi control messages
UPDATE_ALL_CLIENTS = 1
UPDATE_INSTRUMENT_CLIENT = 2
ADD_INSTRUMENT_CLIENT = 3
REMOVE_INSTRUMENT_CLIENT = 4
CHANGE_INSTRUMENT_CLIENT = 5

# Client message types
CLIENT_CONNECT = 1
CLIENT_DISCONNECT = 2
CLIENT_CHECK_CONNECTION = 3
CLIENT_SCENE_MESSAGE = 4

# Server message types
SERVER_CONFIRM_CONNECT = 1
SERVER_CONFIRM_DISCONNECT = 2
SERVER_SCENE_UPDATE = 3
SERVER_CHANGE_SCENE = 4
SERVER_ACTIVATE_CLIENT = 5
SERVER_REMOVE_CLIENT = 6


class ClientManager(object):
    """
      ClientManager

      This class manages the connections to the clients and provides an
      interface to send and receive the messages from
    """

    def __init__(self, graphics_handler):
        self.graphics_handler = graphics_handler
        self.midi_handler = MidiHandler()
        self.client_list = {}  # Maps the clients ID to it's information
        self.active_clients = {}  # Maps a midi channels [1-15] to these designated clients
        self.available_clients = []  # A list of the client ID's that are unassigned

    def handle_message(self, message):
        """

        @param message:
        """
        request = message[0]
        client_address = message[1]
        data = request[0]
        sock = request[1]
        msg_type, client_id = struct.unpack("!BB", data[0:2])

        # Connection
        if msg_type is CLIENT_CONNECT:
            if True:  # if allowed to connect
                initial_msg = self.midi_handler.get_scene_state()
                sock.sendto(initial_msg, (client_address[0], 5555))
                if client_id not in self.client_list:
                    self.client_list[client_id] = client(client_id, (client_address[0], 5555))
                    self.available_clients.append(client_id)

        # Disconnect
        if msg_type is CLIENT_DISCONNECT:
            # Log client out,
            try:
                self.client_list.pop(client_id)
                self.active_clients.pop(client_id)
            except Exception as e:
                print e

        # Maintaining connection state
        if msg_type is CLIENT_CHECK_CONNECTION:
            pass

        # Only scene specific messages are passed through here
        if msg_type is CLIENT_SCENE_MESSAGE:
            if client_id in self.active_clients:
                channel = self.active_clients[client_id]
                self.midi_handler.handle_message(channel, data[2:])

            self.graphics_handler.on_packets_available(client_id, msg_type, data[2:])

    def poll_midi_events(self):
        """
        Constant handling methods here should be universal across the scenes.
        POV of midi_handler
        There is never any knowledge of the state of the clients, client_manager
        should handle cases when there are no clients to become active for example
        """
        events = self.midi_handler.poll_midi_events()
        if events is not None and len(self.client_list) > 0:

            for handle_type, message, channel in events:
                if handle_type is not None:

                    if handle_type is UPDATE_ALL_CLIENTS:

                        for client_id in self.client_list:
                            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                                sendto(message, self.client_list[client_id].address)

                        if channel in self.active_clients:
                            client_id = self.active_clients[channel]
                            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                                sendto(message, self.client_list[client_id].address)

                    elif handle_type is ADD_INSTRUMENT_CLIENT:

                        if channel not in self.active_clients:
                            selected_client_id = self.available_clients.pop()
                            self.active_clients[channel] = selected_client_id

                            message = struct.pack('BB', SERVER_ACTIVATE_CLIENT, message)
                            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                                sendto(message, self.client_list[selected_client_id].address)

                    elif handle_type is REMOVE_INSTRUMENT_CLIENT:

                        if channel in self.active_clients:
                            deactivating_client_id = self.active_clients[channel]
                            self.active_clients.pop(channel)
                            self.available_clients.insert(0, deactivating_client_id)

                            message = struct.pack('BB', SERVER_REMOVE_CLIENT, message)
                            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                                sendto(message, self.client_list[deactivating_client_id].address)

                    elif handle_type is CHANGE_INSTRUMENT_CLIENT:

                        if channel in self.active_clients:
                            deactivating_client_id = self.active_clients[channel]
                            self.active_clients.pop(channel)
                            self.available_clients.insert(0, deactivating_client_id)

                            deactivate_message = struct.pack('BB', SERVER_REMOVE_CLIENT, message[0])
                            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                                sendto(deactivate_message, self.client_list[deactivating_client_id].address)

                        if channel not in self.active_clients:
                            selected_client_id = self.available_clients.pop()
                            self.active_clients[channel] = selected_client_id

                            activate_message = struct.pack('BB', SERVER_ACTIVATE_CLIENT, message[1])
                            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                                sendto(activate_message, self.client_list[selected_client_id].address)
