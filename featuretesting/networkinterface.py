from gevent.server import DatagramServer
import pygame.midi


__author__ = 'Jason'

SERVER_ADDR = ('', 5555)

'''
build a list of the device ids that represent loopback devices
every time a new client is detected,
    create a new interface, assign it a free loopback device from the list
'''


class MidiServer(DatagramServer):
    def __init__(self, *args, **kwargs):
        DatagramServer.__init__(self, *args, **kwargs)
        self.available_devices = list()
        self.client_list = {}
        pygame.midi.init()

    def handle(self, data, address):
        print 'handling packet'
        addr, port = address
        if addr not in self.client_list:
            #Create new ClientInterface for the client
            self.client_list[addr] = ClientInterface(self.availiable_devices.get(), addr)
        self.client_list[addr].trigger(data)

        if data == "stop":
            self.stop()
        else:
            print data


class ClientInterface(object):
    def __init__(self, deviceID, clientID, parser=None):
        self.output = pygame.midi.Output()
        if parser is None:
            self.parser = self.defaultparser
        else:
            self.parser = parser

    def trigger(self, data):
        mididata = self.parser(data)
        self.output.write(mididata)

    def updateParser(self, parser=None):
        if parser is None:
            self.parser = self.defaultparser
        else:
            self.parser = parser

    def defaultparser(data):
        """
        Input:  takes in raw data from the phone client
        Output: 3 element list detailing the 3bytes of a midi message
                described in http://www.indiana.edu/~emusic/etext/MIDI/chapter3_MIDI4.shtml
        Converts the raw data to midi message, this is the default conversion
        though should be customisable by user in a config file
        """
        return [0x80, 127, 127]

