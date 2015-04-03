__author__ = 'jm'

from hydra import log, clientmanager, midihandler

logger = log.get_logger()


class Core(object):
    """
The Core creates and holds a reference to all the neccesary components

ClientManager
    - maintains the list of clients, state of whether is available, as instrument or not etc
    - need to maintain the network session information to track disconnects,
MidiHandler
    - selects the midi inputs/outputs used
    - handles midi messages and directs them to the client manager or they are
    used to set the state of the midi handler
    """

    client_manager = clientmanager.ClientManager()
    midi_handler = midihandler.MidiHandler()

    def __init__(self):
        pass


