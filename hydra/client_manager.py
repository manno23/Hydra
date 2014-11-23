import socket
import struct
from collections import namedtuple

from hydra import midi_handler
from hydra.commands import *

import logging


log = logging.getLogger('Hydra')
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

# Maps the clients ID to it's information
client_list = {}

# Maps the client
instrument_map = InstrumentMapping()

# A list of the client ID's that are unassigned
available_clients = []


def init():
    return midi_handler.MidiHandler()


def handle_message(midi_handler, message):

    request = message[0]
    client_address = message[1]
    data = request[0]
    msg_type, client_id = struct.unpack("!BB", data[0:2])

    if msg_type is CLIENT_CONNECT:

        log.info('Confirming connection with client')
        msg_response_type = struct.pack('B', SERVER_CONFIRM_CONNECT)
        msg = msg_response_type + midi_handler.scene_state()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(msg, ('localhost', 5556))
        sock.close()

        log.info('%s %s' % (client_id, client_address))
        if client_id not in client_list:
            client_list[client_id] = client(client_id, client_address)
            available_clients.append(client_id)

    if msg_type is CLIENT_DISCONNECT:

        log.info('Removing client from lists')
        if client_id in client_list:        client_list.pop(client_id)
        if client_id in available_clients:  available_clients.remove(client_id)
        if client_id in instrument_map.clients:

            channel_changing_client = instrument_map.get_channel(client_id)
            instrument_map.remove_client_id(client_id)

            if len(available_clients) > 0:
                # Swap the instrument to another client if any are available
                selected_client_id = available_clients.pop()
                instrument_map.add(selected_client_id, channel_changing_client)

                # Get state of the instrument to initialise the new client
                instr_state = midi_handler.\
                                get_instrument_state(channel_changing_client)
                msg = CommandAddInstrument(channel_changing_client, 
                                           instr_state).message
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(msg, client_list[selected_client_id].address)
                sock.close()

    if msg_type is CLIENT_INSTRUMENT_MESSAGE:

        log.info('Handling instrument message')
        if client_id in instrument_map.clients:
            channel = instrument_map.get_channel(client_id)
            midi_handler.handle_message(channel, data[2:])

    log.debug(client_list)
    log.debug(available_clients)
    log.debug(instrument_map.channels)


def handle_midi(midi_handler):
    """
    Constant handling methods here should be universal across the scenes.
    POV of midi_handler
    There is never any knowledge of the state of the clients,
    client_manager should handle cases when there are no clients to become
    active for example
    """
    commands = midi_handler.poll_midi_events()
    log.debug('Handling the commands in client_manager')
    log.debug(commands)

    if commands is None or len(client_list) is 0:
        return

    for command in commands:

        if isinstance(command, CommandChangeScene):

            for client_id in available_clients:
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM).\
                    sendto(command.message, ('localhost', 5556))

        elif isinstance(command, CommandUpdateClients):

            for client_id in available_clients:
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                    sendto(command.message, client_list[client_id].address)

        elif isinstance(command, CommandAddInstrument):

            if command.channel not in instrument_map.channels:
                selected_client_id = available_clients.pop()
                instrument_map.add(selected_client_id, command.channel)

                socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                    sendto(command.message,
                           client_list[selected_client_id].address)

        elif (isinstance(command, CommandRemoveInstrument) and
              command.channel in instrument_map.channels):

            deactivating_client_id = \
                instrument_map.get_client_id(command.channel)
            instrument_map.remove_channel(command.channel)
            available_clients.insert(0, deactivating_client_id)

            socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                sendto(command.message,
                       client_list[deactivating_client_id].address)

        elif isinstance(command, CommandChangeClient):

            if command.channel in instrument_map.channels:
                deactivating_client_id = \
                    instrument_map.get_client_id(command.channel)
                instrument_map.remove_channel(command.channel)
                available_clients.insert(0, deactivating_client_id)

                socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                    sendto(command.remove_message,
                           client_list[deactivating_client_id].
                           address)

            if command.channel not in instrument_map.channels:
                selected_client_id = available_clients.pop()
                instrument_map.add(selected_client_id, command.channel)

                socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                    sendto(command.add_message,
                           client_list[selected_client_id].address)

        elif isinstance(command, CommandUpdateInstrument):

            log.debug(client_list)
            log.debug(instrument_map.clients)
            if command.channel in instrument_map.channels:
                client_id = \
                    instrument_map.get_client_id(command.channel)
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM). \
                    sendto(command.message, client_list[client_id].address)


def close():
    client_list = {}
    instrument_map.channels = {}
    instrument_map.clients = {}
    available_clients = []
