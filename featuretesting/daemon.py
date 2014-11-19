import asyncio
import sys
from time import sleep

import pyportmidi as midi

midi.init()

def run():
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.async(read_midi_buffer()),
        asyncio.async(check_input(loop))
    ]

    loop.run_until_complete( asyncio.wait(tasks) )

    loop.close()

@asyncio.coroutine
def read_midi_buffer():
    while True:
        i = midi.Input(1)
        print('checkin')
        yield from i.read(64)

@asyncio.coroutine
def check_input(loop):
    while True:
        yield from sys.stdin.readline()
        if inp[0] is 's':
            loop.stop()
            break


def handler(loop):

    o = midi.Output(0)
    i = midi.Input(1)

    print('Daemon is running')
    while True:

        midi_data = i.read(10)
        network_data = network.read
        keyboard_event = keyboard.read

        process(midi_data, network_data)

run()
