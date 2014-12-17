"""
MidiHandler

Enacts the scene policy by reacting accordingly to scene messages

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
    - Note_on: [116-127] makes the scene [1-12] the current scene.
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

import struct
import logging
import pyportmidi as midi

from hydra.commands import *


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
        self.midi_output = midi.Output(2)
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
        if channel in self.channel_instruments:
            ''' No error message is thrown here as it is not the result of
                a midi input error.
                Possible scenarios are that the midi has removed the instrument
                before the client was updated. '''
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
            log.debug(midi_msgs)
            packets = []
            for midi_msg in midi_msgs:

                status = midi_msg[0][0]
                msg_type = (status & 0b11110000) >> 4
                channel = status & 0b00001111
                data1, data2, data3 = midi_msg[0][1:4]
                # timestamp = midi_msg[1] ignore timestamp

                if channel is 0:
                    packets.append(
                        self.scene_packet(msg_type, channel,
                                          data1, data2, data3))
                else:
                    packets.append(
                        self.instrument_packet(msg_type, channel,
                                               data1, data2, data3))

            return packets

        else:
            return None  # No midi message in the buffer

    def scene_packet(self, msg_type, channel, data1, data2, data3):
        if msg_type is NOTE_ON:

            if data1 > 115:
                # Change the scene from range 0 - 12
                scene_id = data1 - 115
                log.info('Setting scene as ID:%i' % scene_id)
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

        log.info('Updating instrument')
        try:
            update_message = self.channel_instruments[channel].\
                handle_midi(msg_type, channel, data1, data2, data3)
            log.debug(update_message)
            if update_message is not None:
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


class Scene(object):
    """
    Scene

    Each scene specified interprets the messages differently depending
    on how we want the client interface to interact with the midi playing.

    Within a scene messages may be targeted to all clients OR selected clients,
    and the clients targeted may change during the lifetime of the scene.

    The current state of the scene must be maintained here so that all clients
    are reflecting the same model despite their own state.
    """
    def __init__(self, scene_id):
        """
        Default constructor.
        @param scene_id: The ID for the scene that is agreed upon by the
                         clients in the policy.
        @param midi_input: Writes to the virtual midi instrument buffer.
        """
        self.id = scene_id

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        """

        Converts the output midi from the application to the scene specific
        client messages.
        (ie. The scene directs midi to ask the ClientManager to select a
        client, then sends a message to the client to display the its state
        as active, then accept that clients messages and direct these to the
        midi.)

        @param msg_type: single midi message to be interpreted and converted
                         based on the scene policy
        @param channel:
        @param data1:
        @param data2:
        @param data3:
        @param timestamp:
        @return: packed string consisting of the message
                 to be used by the client.

         Also a target_profile, this details what clients to target, when to
         change the targets. The clientmanager manages who the selected clients
         are. If None targets all clients, otherwise each message in list is
         delivered to the selected clients.
        """
        pass

    def scene_state_message(self):
        """
        Compiles all the state of the object and prepares it as a
        message ready for communicating.
        @return: a byte array of the form
        byte[0]: scene id
        byte[1]: the state of the scene, details in the shared policy
        """
        pass


# Example Scenes
class NotActiveScene(Scene):
    def handle_midi(self, msg_type, channel, data1, data2, data3):
        return None

    def scene_state_message(self):
        return struct.pack('B', self.id)


class FountainScene(Scene):
    def __init__(self, scene_id):
        Scene.__init__(self, scene_id)

        # Fountain Scene state determined by incoming
        self.background_white = 1
        self.fountain_speed = 150

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        """
        Kick = []
        Snare = [1]
        A single channel is assigned to every unique voicing

        @param msg_type:
        @param channel:
        @param data1:
        @param data2:
        @param data3:
        @param timestamp:
        @return: Type of message handler which can be of the type,
                     Message to send, with channel specifying the target
                     Update client information,
                        Make client active for channel/instrument, send message
                        Make channel/instrument inactive therefore remove those
                        clients, send message
                 The channel the midi was taken from to determine which clients
                 to send the message to
        """

        if msg_type is NOTE_ON and data1 is 36:
            # Messages for all clients
            self.background_white = not self.background_white
            if self.background_white:
                return struct.pack('BBB', SERVER_SCENE_UPDATE, 0, 0)
            else:
                return struct.pack('BBB', SERVER_SCENE_UPDATE, 0, 1)

        elif msg_type is PITCH_BEND:
            self.fountain_speed = data2
            return struct.pack('BBB', SERVER_SCENE_UPDATE, 1, data2)

        else:
            return None

    def scene_state_message(self):
        return struct.pack('BB',
                           self.background_white,
                           self.fountain_speed)


class ConcentricCircleScene(Scene):
    def __init__(self, scene_id):
        Scene.__init__(self, scene_id)
        self.MSG_HIT = 1

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        if msg_type is NOTE_ON:
            if data1 is 40:
                return struct.pack('B', self.MSG_HIT)
        return None

    def scene_state_message(self):
        return struct.pack('B', self.id)


class Instrument(Scene):
    def __init__(self, instrument_id, midi_output):
        Scene.__init__(self, instrument_id)
        self.midi_output = midi_output

    def handle_message(self, data, channel):
        """
        Converts the scene specific message sent from the client
        to a midi message to be output to the port.

        @param data: byte array sent from the client
        """
        pass


# Example Instruments
class InstrumentFountainScene(Instrument):

    def __init__(self, instrument_id, midi_output):
        Instrument.__init__(self, instrument_id, midi_output)
        self.adding_notes = False
        self.notes_available = []

    def handle_message(self, data, channel):

        melody_player = 1
        volume_control = 2
        note_on, note_off = 1, 2

        msg_type = struct.unpack('B', data[2])

        if msg_type is melody_player:

            # Raise pitch from left to right [0 - 100]
            horizontal_pos, note_state = struct.unpack('BB', data[3:])
            if note_state is note_on:
                note_count = len(self.notes_available)
                div = 100 / note_count
                note_index = horizontal_pos / div
                if note_index >= note_count:
                    note_index = note_count - 1
                note = self.notes_available[note_index]
                print('Note ON:', note)

            elif note_state is note_off:
                print('Note OFF:')

        if msg_type is volume_control:  # Scene output
            # Rotation - determines volume
            self.midi_output.write()
            print('volume control')

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        if msg_type is NOTE_ON:

            # Can now add notes
            if data1 is 0 and not self.adding_notes:
                self.adding_notes = True
            elif data1 is 0 and self.adding_notes:
                return struct.pack('B', len(self.notes_available))
            elif self.adding_notes:
                self.notes_available.append(data1)
                self.notes_available.sort()

    def initial_message(self):
        return struct.pack('BB',
                           SERVER_CONFIRM_CONNECT,
                           self.id)


class InstrumentKeysScene(Instrument):

    def __init__(self, instrument_id, midi_output):
        Instrument.__init__(self, instrument_id, midi_output)

        self.UPDATE_NOTES = 1

        self.adding_notes = False
        self.note_list = []
        self.note_list_buffer = []

    def handle_message(self, data, channel):
        note, note_on = struct.unpack('BB', data)

        if note_on:
            log.info('>>>>> note on', note)
            self.midi_output.note_on(
                self.note_list[note],
                100,
                channel
            )
        else:
            log.info('>>>>> note off', note)
            self.midi_output.note_off(
                self.note_list[note],
                0,
                channel
            )

    def handle_midi(self, msg_type, channel, data1, data2, data3):
        log.info('KeysInstrument handling midi')
        log.debug('msg_type: %s channel: %s data: %s' % (msg_type,
                  channel, data1))
        if msg_type is NOTE_ON:

            # Begin adding notes to the allowable notes
            if data1 is 0 and self.adding_notes is False:

                # Stop any notes that are on
                for note in self.note_list:
                    self.midi_output.note_off(
                        note,
                        0,
                        channel)

                log.info('instrument keys adding notes!')
                self.note_list_buffer = []
                self.adding_notes = True

            elif data1 is 0 and self.adding_notes is True:
                log.info('instrument keys sending new notes!')
                self.adding_notes = False
                self.note_list = self.note_list_buffer
                return struct.pack('BBB', self.id, self.UPDATE_NOTES,
                                   len(self.note_list))

            elif self.adding_notes is True:
                log.info('instrument keys added a note')
                self.note_list_buffer.append(data1)
                self.note_list_buffer.sort()

            return None

    def initial_message(self):
        '''
        The keyboard is initialised with no keys selected
        '''
        return struct.pack('B',
                           self.id,)
