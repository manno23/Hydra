print('@@@@ client_manager')
import socket
import struct
from collections import namedtuple
from hydra.midi_handler import MidiHandler
from hydra.commands import *


client = namedtuple('client', ['id', 'address'])

# Midi control messages
UPDATE_ALL_CLIENTS = 1
ADD_INSTRUMENT_CLIENT = 2
REMOVE_INSTRUMENT_CLIENT = 3
CHANGE_INSTRUMENT_CLIENT = 4
UPDATE_INSTRUMENT_CLIENT = 5

# Client message types
CLIENT_CONNECT = 1
CLIENT_DISCONNECT = 2
CLIENT_CHECK_CONNECTION = 3
CLIENT_INSTRUMENT_MESSAGE = 4


class ClientManager(object):
    """
      ClientManager

      This class manages the connections to the clients and provides an
      interface to send and receive the messages from
    """

    def __init__(self):
        self.midi_handler = MidiHandler()
        '''
        No need to baby user, can create wiki with how to setup virtual
        ports and direct them to the log files that are available to them
        It will not have debug level logging, only above.
        '''

        # Maps the clients ID to it's information
        self.client_list = {}  

        # Maps the client
        self.instrument_map = InstrumentMapping()

        # A list of the client ID's that are unassigned
        self.available_clients = []

    def handle_message(self, message):
        """

        @param message:
        """
        print("handling a message", message)
        request = message[0]
        client_address = message[1]
        data = request[0]
        sock = request[1]
        msg_type, client_id = struct.unpack("!BB", data[0:2])

        # Connection
        if msg_type is CLIENT_CONNECT:
            if True:  # if allowed to connect
                msg_response_type = struct.pack('B', SERVER_CONFIRM_CONNECT)
                msg = msg_response_type + self.midi_handler.scene_state()
                sock.sendto(msg, (client_address[0], 5555))
                if client_id not in self.client_list:
                    self.client_list[client_id] = client(client_id, (client_address[0], 5555))
                    self.available_clients.append(client_id)
            print ('added client')
            print (self.client_list)
            print (self.available_clients)
            print (self.instrument_map.channels)
            print()

        # Disconnect
        if msg_type is CLIENT_DISCONNECT:
            '''
            Second Thoughts:
            We should not be coming back into the midi_handler module purely to create a message
            to be sent to the newly assigned client.
            Handle all of this in the client_manager, because:
            - don't remove the instrument mapping just because no clients are available
            because we need to maintain the state of the instrument
            '''
            # Log client out,
            if client_id in self.client_list:
                self.client_list.pop(client_id)
            if client_id in self.available_clients:
                self.available_clients.remove(client_id)
            if client_id in self.instrument_map.clients:
                # remove the client
                channel_changing_client = self.instrument_map.get_channel(client_id)
                self.instrument_map.remove_client_id(client_id)
                if len(self.available_clients) > 0:
                    # Replace with an available client
                    # then signal that client it is
                    selected_client_id = self.available_clients.pop()
                    self.instrument_map.add(selected_client_id, channel_changing_client)

                    # Get state of the instrument
                    instr_state = self.midi_handler.get_instrument_state(channel_changing_client)
                    msg = CommandAddInstrument(channel_changing_client, instr_state).message
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(msg, self.client_list[selected_client_id].address)

                else:
                    # With no clients to replace it with we can leave it be
                    print ('D: No clients available to represent the instrument')


            print ('removed client')
            print (self.client_list)
            print (self.available_clients)
            print (self.instrument_map.channels)
            print ()

        # Maintaining connection state
        if msg_type is CLIENT_CHECK_CONNECTION:
            pass

        # Only scene specific messages are passed through here
        if msg_type is CLIENT_INSTRUMENT_MESSAGE:
            print ("clientID:", client_id,
                   'channel', self.instrument_map.get_channel(client_id))
            if client_id in self.instrument_map.clients:
                channel = self.instrument_map.get_channel(client_id)
                self.midi_handler.handle_message(channel, data[2:])

# self.graphics_handler.on_packets_available(client_id, msg_type, data[2:])

    def handle_midi(self):
        """
        Constant handling methods here should be universal across the scenes.
        POV of midi_handler
        There is never any knowledge of the state of the clients,
        client_manager should handle cases when there are no clients to become
        active for example
        """
        commands = self.midi_handler.poll_midi_events()

        if commands is None or len(self.client_list) is 0:
            return

        for command in commands:

            if isinstance(command, CommandChangeScene):

                for client_id in self.available_clients:
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM).\
                        sendto(command.message,
                               self.client_list[client_id].address)
                print ('changing scene for clients',
                       self.available_clients)

            elif isinstance(command, CommandUpdateClients):

                for client_id in self.available_clients:
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message, self.client_list[client_id].address)
                print ('updating scene for clients', self.available_clients)

            elif isinstance(command, CommandAddInstrument):

                print ('adding instrument cm')
                if command.channel not in self.instrument_map.channels:
                    selected_client_id = self.available_clients.pop()
                    self.instrument_map.add(selected_client_id, command.channel)
                    print ('added instrument to client')
                    print (self.client_list)
                    print (self.available_clients)
                    print (self.instrument_map.channels)
                    print()

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message, self.client_list[selected_client_id].address)


            elif isinstance(command, CommandRemoveInstrument):

                print ('removing instrument cm')
                if command.channel in self.instrument_map.channels:
                    deactivating_client_id = self.instrument_map.get_client_id(command.channel)
                    self.instrument_map.remove_channel(command.channel)
                    self.available_clients.insert(0, deactivating_client_id)
                    print ('Removing instrument from client', deactivating_client_id)
                    print (self.client_list)
                    print (self.available_clients)
                    print (self.instrument_map.channels)
                    print()

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message, self.client_list[deactivating_client_id].address)

            elif isinstance(command, CommandChangeClient):

                if command.channel in self.instrument_map.channels:
                    deactivating_client_id = \
                        self.instrument_map.get_client_id(command.channel)
                    self.instrument_map.remove_channel(command.channel)
                    self.available_clients.insert(0,
                                                  deactivating_client_id)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.remove_message,
                               self.client_list[deactivating_client_id].
                               address)

                if command.channel not in self.instrument_map.channels:
                    selected_client_id = self.available_clients.pop()
                    self.instrument_map.add(selected_client_id,
                                            command.channel)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.add_message,
                               self.client_list[selected_client_id].address
                               )

            elif isinstance(command, CommandUpdateInstrument):

                if command.channel in self.instrument_map.channels:
                    client_id = \
                        self.instrument_map.get_client_id(command.channel)
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message, self.client_list[client_id].address)
                    print ('updating client', client_id)


class InstrumentMapping():
    def __init__(self):
        self.channels = {}
        self.clients = {}

    def add(self, client_id, channel):
        self.channels[channel] = client_id
        self.clients[client_id] = channel

    def get_channel(self, client_id):
        return self.clients[client_id]

    def get_client_id(self, channel):
        return self.channels[channel]

    def remove_channel(self, channel):
        client_id = self.channels.pop(channel)
        self.clients.pop(client_id)

    def remove_client_id(self, client_id):
        channel = self.clients.pop(client_id)
        self.channels.pop(channel)
