from pygame import midi

__author__ = 'Jason'

class MidiHandler(object):
    def __init__(self):
        midi.init()
        self.device = midi.Output(4)

    def handle(self, type, **data):
        if type == 1.0:
            if data['out'] == 1.0:
                self.device.note_on(64, 100)
        elif type == 2.0:
            y = (data['y'] + 50)/2
            if y > 127:
                y = 127
            print y
            self.device.write([[[0xE0, int(y*2), int(y*2)],1], ])