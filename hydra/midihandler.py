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
"""
import struct
from pygame import midi
from pyglet import gl
import client_manager
from graphics import rot_mat_to_angle

__author__ = 'Jason'

# Midi msg constants
NOTE_OFF = 8
NOTE_ON = 9
PITCH_BEND = 14

"""
MidiHandler

Communication policy
MIDI INPUTS:
Channel 0: Directs all midi messages to the active scene.
           - Note_on: [116-127] makes the scene [1-12] the current scene.
           - All other midi messages are availble for use by the scenes
           - No inputs from the clients is received onto this channel, it only receives messages
             to update its display

Channel 1-15: Directs midi messages to the instruments.
              - Note_on: [121 - 125] signal to assign the instrument [1-5] to the channel. A client
              will be selected from the available clients and assigned as a controller to this instrument.
              - Not3\e_on: [126] will remove the instrument from the channel and signal the assigned client
              that it is not active, reverting it to the current scene.
              - Note_on: [127] swaps the client assigned to the channel/instrument
              -  All other notes are available to the instrument to do as it pleases eg.
                * Modify the way the client interacts with the instrument,
                    ie. adding new notes to play, allowing volume control
                * Update the visuals on the client

Channel 15: Changes the current scene

"""
class MidiHandler(object):
    def __init__(self):
        midi.init()
        self.midi_input = midi.Output(4)
        self.midi_output = midi.Input(1)

        # Create scenes
        self.scene_list = {}
        self.scene_list[1] = FountainScene(1, self.midi_input)

        self.instrument_list = {}
        self.instrument_list[1] = InstrumentFountainScene

        # Maps an instrument to a channel
        self.channel_instrument = {}

        # Initiate scene 1 to start off with
        self.current_scene = self.scene_list[1]
        self.current_scene_id = 1

    def change_scene(self, scene_id):
        try:
            self.current_scene = self.scene_list[scene_id]
            self.current_scene_id = scene_id
        except KeyError:
            print 'The scene ID [' + str(scene_id) + '] chosen by the midi on channel 0 is not available.'
            print 'Possible scenes are', self.scene_list

    def handle_message(self, channel, data):
        if channel is 0:
            self.current_scene.handle_client_message(data)
        else:
            if self.channel_instrument.has_key(channel):
                # No error message is thrown here as it is not the result of a midi input error.
                # Possible scenarios are that the midi has removed the instrument before the client was updated.
                self.channel_instrument[channel].handle_message(data)

    def poll_midi_events(self):
        """
        Polls the midi message buffer and takes from it 1 message at a time.
        @return: A byte array in string form containing a message
                in adherence with the communication policy.
        """
        if self.midi_output.poll():

            midi_msgs = self.midi_output.read(20)
            packets = []
            for midi_msg in midi_msgs:

                status = midi_msg[0][0]
                msg_type = (status & 0b11110000) >> 4
                channel = status & 0b00001111
                data1, data2, data3 = midi_msg[0][1:4]
                timestamp = midi_msg[1]


                # Scene channel
                if channel is 0:

                    if msg_type is NOTE_ON:

                        if data1 > 115:
                            # Change the scene from range 0 - 12
                            scene_id = data1 - 115
                            self.change_scene(scene_id)
                            packets.append(
                                (
                                    client_manager.UPDATE_ALL_CLIENTS,
                                    struct.pack('BB', client_manager.SERVER_CHANGE_SCENE, scene_id),
                                    0
                                )
                            )
                        else:
                            packets.append(
                                self.current_scene.handle_midi(msg_type, channel, data1, data2, data3, timestamp)
                            )

                # Instrument channels
                else:

                    if msg_type is NOTE_ON:

                        # Define notes available to play
                        if data1 is 126:
                            try:
                                packets.append(
                                    (
                                        client_manager.REMOVE_INSTRUMENT_CLIENT,
                                        self.current_scene_id,
                                        channel
                                    )
                                )
                            except KeyError:
                                print 'Cannot remove an instrument if none has been assigned.'

                        elif data1 is 127:
                            try:
                                packets.append(
                                    (
                                        client_manager.CHANGE_INSTRUMENT_CLIENT,
                                        (self.current_scene_id, self.channel_instrument[channel].instrument_id),
                                        channel
                                    )
                                )
                            except KeyError:
                                print 'Cannot change client on the channel ' + str(channel) + 'when no instrument has been assigned.'
                                print 'Assign an instrument first from the midi input range 121 - 125.'

                        elif data1 > 120:
                            instrument_id = data1 - 120
                            self.channel_instrument[channel] = self.new_instrument(instrument_id)
                            packets.append(
                                (
                                    client_manager.ADD_INSTRUMENT_CLIENT,
                                    instrument_id,
                                    channel
                                )
                            )

                        # send instrument midi to the instrument object to handle
                        # it must have been created for this to occur
                        else:
                            try:
                                packets.append(
                                    self.channel_instrument[channel].handle_midi(msg_type, channel, data1, data2, data3, timestamp)
                                )
                            except KeyError:
                                print 'The instrument has not been created for this channel'


            return packets

        else:
            # No midi message in the buffer
            return None

    def get_scene_state(self):
        return self.current_scene.create_client_initialisation_message()

    def new_instrument(self, instrument_type):
        """
        Factory method that returns a new instrument object of the specified
        type.
        @return: Instrument object
        """
        return self.instrument_list[instrument_type](instrument_type, self.midi_input)

    def select_midi_ports(self):
        return midi.Input(1), midi.Output(4)



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
    def _init__(self, scene_id, midi_input):
        """
        Default constructor.
        @param scene_id: The ID for the scene that is agreed upon by the clients in the policy.
        @param midi_input: Writes to the virtual midi instrument buffer.
        """
        pass

    def handle_midi(self, msg_type, channel, data1, data2, data3, timestamp):
        """

        Converts the output midi from the application to the scene specific
        client messages.
        (ie. The scene directs midi to ask the ClientManager to select a client,
        then sends a message to the client to display the its state as active,
        then accept that clients messages and direct these to the midi.)

        @param msg_type: single midi message to be interpreted and converted based on the scene policy
        @param channel:
        @param data1:
        @param data2:
        @param data3:
        @param timestamp:
        @return: packed string consisting of the message to be used
                 by the client.
                 the channel/instrument the midi_message was derived from determines
                 Also a target_profile, this details what clients to target, when to
                 change the targets. The clientmanager manages who the selected clients are.
                 if None targets all clients, otherwise each message in list is delivered to
                 the selected clients.
        """
        pass

    def create_current_state_message(self):
        """
        Compiles all the state of the object and prepares it as a
        message ready for communicating.
        @return: a byte array in string form for sending from a socket
        """
        pass


# Example Scenes
class FountainScene(Scene):
    def __init__(self, scene_id, midi_input):
        self.scene_id = scene_id
        self.midi_input = midi_input

        # Fountain Scene state determined by incoming
        self.background_white = True
        self.fountain_speed = 15

    def handle_midi(self, msg_type, channel, data1, data2, data3, timestamp):
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
                        Make channel/instrument inactive therefore remove those clients, send message
                 The channel the midi was taken from, to determine which clients to
                 send the message to
        """

        if msg_type is NOTE_ON and data1 is 36:
        # Messages for all clients
            self.background_white = not self.background_white
            if self.background_white:
                return client_manager.UPDATE_ALL_CLIENTS,\
                       struct.pack('BBB', client_manager.SERVER_SCENE_UPDATE, 0, 0),\
                       channel
            else:
                return client_manager.UPDATE_ALL_CLIENTS,\
                       struct.pack('BBB', client_manager.SERVER_SCENE_UPDATE, 0, 1),\
                       channel

        elif msg_type is PITCH_BEND:
            self.fountain_speed = data2
            return client_manager.UPDATE_ALL_CLIENTS,\
                   struct.pack('BBB', client_manager.SERVER_SCENE_UPDATE, 1, data2),\
                   channel

        else:
            return None, None, None

    def create_client_initialisation_message(self):
        return struct.pack('BBBB',
                           client_manager.SERVER_CONFIRM_CONNECT,               # connection
                           self.scene_id,           # initial scene
                           int(self.background_white),
                           int(self.fountain_speed)
        )


class Instrument(Scene):

    def handle_client_message(self, data):
        """
        Converts the scene specific message sent from the client
        to a midi message to be output to the port.

        @param data: byte array sent from the client
        """
        pass


# Example Instruments
class InstrumentFountainScene(Instrument):

    def __init__(self, instrument_id, midi_input):
        self.instrument_id = instrument_id
        self.midi_input = midi_input
        self.adding_notes = False
        self.notes_available = []

    def handle_client_message(self, data):

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
                print 'Note ON:', note

            elif note_state is note_off:
                print 'Note OFF:'


        if msg_type is volume_control:  # Scene output
            # Rotation - determines volume
            out = struct.unpack('!16f', data)
            rot_matrix = (gl.GLfloat * len(out))(*out)
            x, y, z = rot_mat_to_angle(rot_matrix)
            print 'volume control'

    def handle_midi(self, msg_type, channel, data1, data2, data3, timestamp):
        if msg_type is NOTE_ON:

            # Can now add notes
            if data1 is 0:
                self.adding_notes = not self.adding_notes
            else:
                self.notes_available.append(data1)
                self.notes_available.sort()

    def create_current_state_message(self):
        return struct.pack('BB',
                           client_manager.SERVER_CONFIRM_CONNECT,
                           self.instrument_id
        )

