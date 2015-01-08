__author__ = 'Jason'
from hydra.scenes import Scene

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
        self.volume_level = 0

    def handle_message(self, data, channel):

        melody_player = 1
        volume_control = 2
        note_on, note_off = 1, 2

        msg_type, = struct.unpack('B', data[0:1])
        log.debug("fountain msg: %i %s" % (msg_type, data[1:]))

        if msg_type is melody_player and \
                        len(self.notes_available) is not 0:

            # Raise pitch from left to right [0 - 100]
            horizontal_pos, note_state = struct.unpack('BB', data[1:3])
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
            azimuth, pitch, roll = struct.unpack('!fff', data[1:13])
            log.debug("x: %f, y: %f" % (pitch, roll))

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
