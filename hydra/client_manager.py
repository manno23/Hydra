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

import sys
import socket
import struct
from collections import namedtuple

from hydra.commands import (
    SERVER_CONFIRM_CONNECT,
    CommandChangeScene,
    CommandUpdateClients,
    CommandAddInstrument,
    CommandRemoveInstrument,
    CommandChangeClient,
    CommandUpdateInstrument
    )

import logging

sh = logging.StreamHandler(sys.stdout)

log = logging.getLogger('Hydra')
log.setLevel(logging.DEBUG)
log.addHandler(sh)

client = namedtuple('client', ['id', 'address', ])

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

# HYDRAHEAD Destination port
DESTINATION_NET_PORT = 23232


class ClientManager():

    def __init__(self):

        self._instrument_map = InstrumentMapping()  # Maps the client
        self._client_list = {}  # Maps the clients ID to it's information
        self._available_clients = []  # list of unassigned client IDs

    def handle_message(self, mh, message):

        data = message[0][0]
        client_address = message[1][0]
        msg_type, client_id = struct.unpack("!BB", data[0:2])

        log.debug(message)
        log.debug(client_address)

        if msg_type is CLIENT_CONNECT:

            log.info('Confirming connection with client')
            msg_response_type = struct.pack('B', SERVER_CONFIRM_CONNECT)
            msg = msg_response_type + mh.scene_state()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg, (client_address, DESTINATION_NET_PORT))
            sock.close()

            if client_id not in self._client_list:
                self._client_list[client_id] = client(client_id,
                                                      client_address)
                self._available_clients.append(client_id)

        if msg_type is CLIENT_DISCONNECT:

            log.info('Removing client from lists')
            if client_id in self._client_list:
                self._client_list.pop(client_id)
            if client_id in self._available_clients:
                self._available_clients.remove(client_id)
            if client_id in self._instrument_map.clients:

                channel_changing_client = self._instrument_map.\
                    get_channel(client_id)
                self._instrument_map.remove(client_id)

                if len(self._available_clients) > 0:
                    # Swap the instrument to another client if any available
                    selected_client_id = self._available_clients.pop()
                    self._instrument_map.add(selected_client_id,
                                             channel_changing_client)

                    # Get state of the instrument to initialise the new client
                    instr_state = mh.\
                        get_instrument_state(channel_changing_client)
                    msg = CommandAddInstrument(channel_changing_client,
                                               instr_state).message
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(msg,
                                self._client_list[selected_client_id].address)
                    sock.close()

        if msg_type is CLIENT_INSTRUMENT_MESSAGE:

            log.info('Handling instrument message')
            if self.client_id in self._instrument_map.clients:
                channel = self._instrument_map.get_channel(self.client_id)
                mh.handle_message(channel, data[2:])

    def handle_midi(self, mh):
        """
        Constant handling methods here should be universal across the scenes.
        POV of midi_handler
        There is never any knowledge of the state of the clients,
        self.client_manager should handle cases when there are no clients to
        become active for example
        """
        commands = mh.poll_midi_events()

        if commands is None or len(self._client_list) is 0:
            return

        for command in commands:

            if isinstance(command, CommandChangeScene):

                for client_id in self._available_clients:
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM).\
                        sendto(command.message,
                               (self._client_list[client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandUpdateClients):

                for client_id in self._available_clients:
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message,
                               (self._client_list[client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandAddInstrument):

                if command.channel not in self._instrument_map.channels:

                    selected_client_id = self._available_clients.pop()
                    self._instrument_map.add(selected_client_id,
                                             command.channel)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message,
                               (self._client_list[selected_client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandRemoveInstrument):

                if command.channel in self._instrument_map.channels:

                    deactivating_client_id = \
                        self._instrument_map.get_client_id(command.channel)
                    self._instrument_map.remove_channel(command.channel)
                    self._available_clients.insert(0,
                                                   deactivating_client_id)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message,
                               (self._client_list[deactivating_client_id]
                                   .address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandChangeClient):

                if command.channel in self._instrument_map.channels:

                    deactivating_client_id = \
                        self._instrument_map.get_client_id(command.channel)

                    self._instrument_map.remove_channel(command.channel)
                    self._available_clients.insert(0,
                                                   deactivating_client_id)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.remove_message,
                               (self._client_list[deactivating_client_id]
                                   .address,
                                DESTINATION_NET_PORT))

                else:

                    selected_client_id = self._available_clients.pop()
                    self._instrument_map.add(selected_client_id,
                                             command.channel)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.add_message,
                               (self._client_list[selected_client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandUpdateInstrument):

                if command.channel in self._instrument_map.channels:
                    client_id = \
                        self._instrument_map.get_client_id(command.channel)
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message, (self._client_list[client_id]
                                                 .address,
                                                 DESTINATION_NET_PORT))

    def close(self):
        self._client_list = {}
        self._available_clients = []
        self._instrument_map.channels = {}
        self._instrument_map.clients = {}


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
