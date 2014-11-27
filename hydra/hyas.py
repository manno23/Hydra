import asyncio
import pyportmidi as midi
from hydra.midi_handler import MidiHandler
from hydra.client_manager import handle_midi, handle_message


MIDI_FREQUENCY = 5


# Need to create a data structure that will be able to share function results
# among each other


def run():

    midi.init()

    msg_queue = asyncio.queues.Queue()
    loop = asyncio.get_event_loop()
    midi_object = MidiHandler()

    midi_task = loop.create_task(check_midi(midi_object))
    network_task = loop.create_task(check_network(midi_object, msg_queue))
    listen = loop.create_datagram_endpoint(
        HydraProtocol(msg_queue), local_addr=('127.0.0.1', 5555))
    l = loop.create_task(listen)

    tasks = [l, midi_task, network_task]
    print(tasks)

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as e:
        print(e)

    try:
        print('running loop')
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    loop.close()


def stop():
    pass


@asyncio.coroutine
def check_midi(midi_object):
    while True:
        yield from asyncio.sleep(1./float(MIDI_FREQUENCY))
        handle_midi(midi_object)


@asyncio.coroutine
def check_network(midi_object, msg_queue):
    while True:
        try:
            network_data = yield from msg_queue.get()
            print(network_data)
            handle_message(midi_object, network_data)
        except Exception as e:
            print(e)


class HydraProtocol(asyncio.DatagramProtocol):
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        print("initialised with msg_queue %s" % self.msg_queue)

    def connection_lost(self):
        print("connection lost")

    def datagram_received(self, data, addr):
        print("received data: ", data, "from ", addr)
        self.msg_queue.put_nowait(data)

    def error_received(self, exc):
        print("There was an error sending/receiving")
        print(exc)

    def pause_writing(self):
        print("The output buffer has been filled")

    def resume_writing(self):
        print("OS Signaled! Can now write to the buffer again")
