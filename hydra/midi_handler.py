"""
MidiHandler

Enacts the scene policy by reacting accordingly to scene/instrument messages

the number of instruments needed for each scene must be

The received midi commands belong to the fields,
scene change
scene specific messages
    these are of the fields,
      to update the clients graphically.
      to direct at certain targets

Communication policy
MIDI INPUTS:
Channel 0: Directs all midi messages to the active scene.
    - Note_on: [1-12] makes the scene [1-12] the current scene.
    - All other midi messages are availble for use by the scenes.
    - No inputs from the clients is received onto this channel, it only
      receives messages to update its display.

Channel 1-15: Directs midi messages to the instruments.
    - Note_on: [121 - 125] signal to assign the instrument[1-5] to the channel.
      A client will be selected from the available clients and assigned as a
      controller to this instrument.
    - Note_on: [126] will remove the instrument from the channel and signal the
      assigned client that it is not active, reverting it to the current scene.
    - Note_on: [127] swaps the client assigned to the channel/instrument
    - All other notes are available to the instrument to do as it pleases eg.
        * Modify the way the client interacts with the instrument,
          ie. adding new notes to play, allowing volume control
        * Update the visuals on the client

Channel 15: Changes the current scene
"""

import logging
import pyportmidi as midi

from hydra.commands import *
from hydra.scenes import *
from hydra.instruments import *


__author__ = 'Jason'


# Midi msg constants
NOTE_OFF = 8
NOTE_ON = 9
PITCH_BEND = 14


log = logging.getLogger('Hydra')
log.setLevel(logging.DEBUG)


class MidiHandler(object):
    """
    MidiHandler

    """
    def __init__(self):

        midi.init()
        self.midi_output = midi.Output(5)
        self.midi_input = midi.Input(1)

        # Index Scenes
        self.scene_list = {}
        self.scene_list[0] = NotActiveScene(0)
        self.scene_list[1] = FountainScene(1)
        self.scene_list[2] = ConcentricCircleScene(2)

        # Index Instruments
        self.instrument_list = {}
        self.instrument_list[1] = InstrumentFountainScene
        self.instrument_list[2] = InstrumentKeysScene

        # Maps an instrument to a channel
        self.channel_instruments = {}
        # Initialise scene to NotActiveScene
        self.current_scene = self.scene_list[0]

    def scene_state(self):
        """

        @return: If a scene is active, detail the current scene ID and its
        state to the client. If no scene is active, no msg is required.
        """
        return self.current_scene.scene_state_message()

    def handle_message(self, channel, data):
        ''' No error message is thrown here as it is not the result of
            a midi input error.
            Possible scenarios are that the midi has removed the instrument
            before the client was updated. '''
        if channel in self.channel_instruments:
            self.channel_instruments[channel].handle_message(data, channel)

    def poll_midi_events(self):
        """
        Polls the midi message buffer and takes from it 1 message at a time.
        Each midi message is then put into a list as a batch job for the client
        manager, or is used to update the state of the midi instruments/scenes.

        @return: a list of commands for the clientManager.
            Each command consists of:
                command[0]: type of command
                command[1]: message to be sent to clients (if neccesary)
                command[2]: the channel the midi command derived from.
        """
        if self.midi_input.poll():

            midi_msgs = self.midi_input.read(32)
            packets = []
            for midi_msg in midi_msgs:

                status = midi_msg[0][0]
                msg_type = (status & 0b11110000) >> 4
                channel = status & 0b00001111
                data1, data2, data3 = midi_msg[0][1:4]
                # timestamp = midi_msg[1] ignore timestamp
                # log.debug("%i %i %i %i %i" % (msg_type, channel, data1, data2, data3))

                if channel is 0:
                    packets.append(
                        self.scene_packet(msg_type, channel,
                                          data1, data2, data3))
                else:
                    packets.append(
                        self.instrument_packet(msg_type, channel,
                                               data1, data2, data3))

            # log.debug("\n")
            return packets

        else:
            return None  # No midi message in the buffer

    def scene_packet(self, msg_type, channel, data1, data2, data3):
        if msg_type is NOTE_ON:

            if data1 < 12:
                # Change the scene from range 0 - 12
                scene_id = data1
                log.info('Setting scene as ID: %i' % scene_id)
                try:
                    self.change_scene(scene_id)
                    return CommandChangeScene(scene_id,
                                              self.current_scene.
                                              scene_state_message())
                except KeyError:
                    print('The scene ID [' + str(scene_id) +
                          '] chosen by the midi on channel 0 is not available')
                    print('Possible scenes are', self.scene_list)
                    logging.error('Attempted to set a scene id' +
                                  'that is out of range.')
            else:
                scene_msg = self.current_scene.handle_midi(msg_type,
                                                           channel,
                                                           data1,
                                                           data2,
                                                           data3)
                if scene_msg is not None:
                    return CommandUpdateClients(scene_msg)

    def instrument_packet(self, msg_type, channel, data1, data2, data3):

        if msg_type is NOTE_ON:

            if data1 is 127:
                # Change the client associated with the instrument
                # on this channel
                try:
                    instrument = self.channel_instruments[channel]
                    if instrument is not None:
                        return \
                            CommandChangeClient(
                                channel,
                                self.current_scene.id,
                                instrument.initial_message()
                            )
                except KeyError:
                    log.error('Cannot change client on the channel %s ' +
                              'when no instrument has been assigned.\n' +
                              'Assign an instrument first from the midi ' +
                              'input range 121 - 125.')

            elif data1 is 126:

                log.info('Unmapping instrument from channel')
                try:
                    print(self.channel_instruments)
                    self.channel_instruments.pop(channel)
                    print(self.channel_instruments)
                    print()
                    return CommandRemoveInstrument(
                        channel,
                        self.current_scene.id,
                        self.current_scene.scene_state_message())
                except KeyError:
                    log.error('Cannot remove an instrument if none has been \
                          assigned.')

            elif data1 > 120:
                instrument_id = data1 - 120
                log.info('Mapping instrument %i to the channel.' %
                         instrument_id)
                if instrument_id in self.instrument_list:

                    if ((channel in self.channel_instruments) and
                        (self.channel_instruments[channel].id is not instrument_id)) \
                            or \
                       (channel not in self.channel_instruments):

                        self.channel_instruments[channel] = \
                            self.new_instrument(instrument_id)
                        message = self.channel_instruments[channel].\
                            initial_message()
                        return CommandAddInstrument(channel, message)

        try:
            update_message = self.channel_instruments[channel].\
                handle_midi(msg_type, channel, data1, data2, data3)
            if update_message is not None:
                log.debug(update_message)
                return CommandUpdateInstrument(
                    channel,
                    update_message)

        except KeyError:
            log.error('No instrument has been created for the channel')

    def change_scene(self, scene_id):
        self.current_scene = self.scene_list[scene_id]

    def new_instrument(self, instrument_type):
        """
        Factory method that returns a new instrument object of the specified
        type.
        @return: Instrument object
        """
        return self.instrument_list[instrument_type](instrument_type,
                                                     self.midi_output)

    def get_instrument_state(self, channel):
        self.channel_instruments.get(channel).initial_message()
