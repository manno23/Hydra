import time
import random
import gevent
import pygame.midi
from gevent.queue import LifoQueue
from Queue import deque
from mididata import data

MIDI_RATE = 1/64

packet_buffer = LifoQueue(10)

class Actor(gevent.Greenlet):
    def __init__(self):
        self.buffer = LifoQueue()
        gevent.Greenlet.__init__(self)
    def receive(self, message):
        raise NotImplemented
    def _run(self):
        self.running = True
        while self.running:
            message = self.buffer.get()
            self.receive(message)

class MidiInterface(Actor):
    '''
receive - This performs the midi operation
    '''
    def __init__(self):
        pygame.midi.init()
        self.device_id = 0
        for i in xrange(pygame.midi.get_count()):
            (interface, name, input, output, opened) = pygame.midi.get_device_info(i)
            if name == '01. Internal MIDI':
                self.device_id = interface
        self.device = pygame.midi.Output(4)
        Actor.__init__(self)

    def receive(self, message):
        print 'note on'
        self.device.write([[message,0], ])
        gevent.sleep(MIDI_RATE)

class NetworkSimulator(gevent.Greenlet):
    def __init__(self):
        self.pitchvalues = deque()
        self.pitchvalues.extend([0xE0, n, n] for n in range(127))
        self.pitchvalues.extend([0xE0, n, n] for n in range(127,False,-1))
        gevent.Greenlet.__init__(self)
    def _run(self):
        while True:
            message = self.pitchvalues.popleft()
            midi.buffer.put(self.pitchvalues.popleft())
            gevent.sleep(0.05)

midi = MidiInterface()
net = NetworkSimulator()

midi.start(); net.start()

gevent.joinall([midi, net])
