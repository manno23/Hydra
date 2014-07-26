import struct

SERVER_CONFIRM_CONNECT = 1
SERVER_CONFIRM_DISCONNECT = 2
SERVER_SCENE_UPDATE = 3
SERVER_CHANGE_SCENE = 4
SERVER_ACTIVATE_CLIENT = 5
SERVER_REMOVE_CLIENT = 6
SERVER_UPDATE_INSTRUMENT = 7


class CommandChangeScene():
    def __init__(self, scene_id, initialisation_msg):
        self.message = struct.pack('BB', SERVER_CHANGE_SCENE, scene_id) + initialisation_msg

class CommandUpdateClients():
    """
    Messages directed to all clients do not require updates of the
    ClientManagers state, therefore they all fall under the same command.
    """
    def __init__(self, message):
        self.message = message

class CommandAddInstrument():
    def __init__(self, channel, initialising_state):
        self.channel = channel
        self.message = struct.pack('B', SERVER_ACTIVATE_CLIENT) + initialising_state

class CommandRemoveInstrument():
    """
    @param message the message will require that t
    """
    def __init__(self, channel, current_scene_id, initialising_state):
        self.channel = channel
        self.current_scene_id = current_scene_id
        self.message = struct.pack('BB', SERVER_REMOVE_CLIENT, current_scene_id) + initialising_state

class CommandChangeClient():
    def __init__(self, channel, current_scene_id, initialising_state):
        self.channel = channel
        self.remove_message = struct.pack('BB', SERVER_REMOVE_CLIENT, current_scene_id)
        self.add_message = struct.pack('B', SERVER_ACTIVATE_CLIENT) + initialising_state

class CommandUpdateInstrument():
    def __init__(self, channel, instrument_update_message):
        self.message = struct.pack('B', SERVER_UPDATE_INSTRUMENT )+ instrument_update_message
        self.channel = channel

