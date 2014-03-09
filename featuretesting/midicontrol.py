import sys
import os

import pygame
import pygame.midi
import time
from pygame.locals import *

def _print_device_info():
    for i in xrange( pygame.midi.get_count() ):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print ("%2i: interface :%s:, name :%s:, opened:%s:  %s" %
               (i, interf, name, opened, in_out))

if __name__ == '__main__':
    pygame.midi.init()
    _print_device_info()

    time.sleep(2)

    midiout = pygame.midi.Output(4)
    midiout.note_on(48, velocity=40)
    midiout.note_on(42, velocity=40)
    time.sleep(2)
    midiout.note_off(48)
    midiout.note_off(42)
    pygame.midi.quit()
