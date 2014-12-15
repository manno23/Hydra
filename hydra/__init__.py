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

__version__ = '0.0.1'
__author__ = 'Jason Manning'

import sys
import socket
import struct
from collections import namedtuple

from hydra import midi_handler
from hydra.commands import *

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

'''
No need to baby user, can create wiki with how to setup virtual
ports and direct them to the log files that are available to them
It will not have debug level log, only above.
'''


class ClientManager():

    def __init__(self):

        self.client_list = {}  # Maps the clients ID to it's information
        self.instrument_map = InstrumentMapping()  # Maps the client
        self.available_clients = []  # A list of the client ID's that are unassigned

    def handle_message(self, message):

        data = message[0][0]
        self.client_address = message[1][0]
        msg_type, self.client_id = struct.unpack("!BB", data[0:2])

        log.debug(message)
        log.debug(self.client_address)

        if msg_type is CLIENT_CONNECT:

            log.info('Confirming connection with client')
            msg_response_type = struct.pack('B', SERVER_CONFIRM_CONNECT)
            msg = msg_response_type + midi_handler.scene_state()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg, (self.client_address, DESTINATION_NET_PORT))
            sock.close()

            if self.client_id not in client_list:
                self.client_list[client_id] = client(client_id, client_address)
                self.available_clients.append(self.client_id)

        if msg_type is CLIENT_DISCONNECT:

            log.info('Removing client from lists')
            if self.client_id in client_list:
                self.client_list.pop(client_id)
            if self.client_id in self.available_clients:
                self.available_clients.remove(self.client_id)
            if self.client_id in self.instrument_map.clients:

                channel_changing_client = self.instrument_map.\
                    get_channel(self.client_id)
                self.instrument_map.remove_self.client_id(client_id)

                if len(self.available_clients) > 0:
                    # Swap the instrument to another client if any available
                    selected_self.client_id = self.available_clients.pop()
                    self.instrument_map.add(selected_self.client_id,
                                            channel_changing_client)

                    # Get state of the instrument to initialise the new client
                    instr_state = midi_handler.\
                        get_instrument_state(channel_changing_client)
                    msg = CommandAddInstrument(channel_changing_client,
                                               instr_state).message
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.sendto(msg,
                                self.client_list[selected_client_id].address)
                    sock.close()

        if msg_type is CLIENT_INSTRUMENT_MESSAGE:

            log.info('Handling instrument message')
            if self.client_id in self.instrument_map.clients:
                channel = self.instrument_map.get_channel(self.client_id)
                midi_handler.handle_message(channel, data[2:])

    def handle_midi(self, midi_handler):
        """
        Constant handling methods here should be universal across the scenes.
        POV of midi_handler
        There is never any knowledge of the state of the clients,
        self.client_manager should handle cases when there are no clients to
        become active for example
        """
        commands = midi_handler.poll_midi_events()

        if commands is None or len(self.client_list) is 0:
            return

        for command in commands:

            if isinstance(command, CommandChangeScene):

                for self.client_id in self.available_clients:
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM).\
                        sendto(command.message,
                               (self.client_list[client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandUpdateClients):

                for self.client_id in self.available_clients:
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message,
                               (self.client_list[client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandAddInstrument):

                if command.channel not in self.instrument_map.channels:

                    selected_self.client_id = self.available_clients.pop()
                    self.instrument_map.add(selected_self.client_id,
                                            command.channel)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message,
                               (self.client_list[selected_client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandRemoveInstrument):

                if command.channel in self.instrument_map.channels:

                    deactivating_self.client_id = \
                        self.instrument_map.get_self.client_id(command.channel)
                    self.instrument_map.remove_channel(command.channel)
                    self.available_clients.insert(0,
                                                  deactivating_self.client_id)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message,
                               (self.client_list[deactivating_client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandChangeClient):

                if command.channel in self.instrument_map.channels:

                    deactivating_self.client_id = \
                        self.instrument_map.get_self.client_id(command.channel)

                    self.instrument_map.remove_channel(command.channel)
                    self.available_clients.insert(0,
                                                  deactivating_self.client_id)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.remove_message,
                               (self.client_list[deactivating_client_id].address,
                                DESTINATION_NET_PORT))

                else:

                    selected_self.client_id = self.available_clients.pop()
                    self.instrument_map.add(selected_self.client_id,
                                            command.channel)

                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.add_message,
                               (self.client_list[selected_client_id].address,
                                DESTINATION_NET_PORT))

            elif isinstance(command, CommandUpdateInstrument):

                if command.channel in self.instrument_map.channels:
                    self.client_id = \
                        self.instrument_map.get_self.client_id(command.channel)
                    socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                        sendto(command.message, (self.client_list[client_id].address,
                                                 DESTINATION_NET_PORT))

    def close(self):
        self.client_list = {}
        self.instrument_map.channels = {}
        self.instrument_map.clients = {}
        self.available_clients = []
