__author__ = 'jason'

VERSION = "0.1 alpha"


def get_version():
    """
    :return: printable string of version information
    """
    return VERSION


def windows_check():
    return False


def osx_check():
    return False


# MESSAGE TYPES
class MidiMsg():
    def __init__(self):
        self.NOTE_OFF = 8
        self.NOTE_ON = 9
        self.PITCH_BEND = 1

class ServerMsg():
    def __init__(self):
        self.UPDATE_ALL_CLIENTS = 1
        self.ADD_INSTRUMENT_CLIENT = 2
        self.REMOVE_INSTRUMENT_CLIENT = 3
        self.CHANGE_INSTRUMENT_CLIENT = 4
        self.UPDATE_INSTRUMENT_CLIENT = 5

class ClientMsg():
    def __init__(self):
        self.CONNECT = 1
        self.DISCONNECT = 2
        self.CHECK_CONNECTION = 3
        self.INSTRUMENT_MESSAGE = 4


# ERRORS
class DaemonRunningError(object):
    pass