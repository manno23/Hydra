import asyncio
import pyportmidi as midi

from hydra.client_manager import handle_midi, handle_message


MIDI_FREQUENCY = 15


@asyncio.coroutine
def check_queue(input_socket):
    while True:
        yield from asyncio.sleep(1./float(MIDI_FREQUENCY))
        midi_data = input_socket.read(32)
        client_manager.handle_midi(midi_data)


def run():
    midi.init()
    input_socket = midi.Input(1)
    loop = asyncio.get_event_loop()

    check = loop.create_task(check_queue(input_socket))
    listen = loop.create_datagram_endpoint(
        HydraProtocol, local_addr=('127.0.0.1', 5555))

    tasks = [check, listen]
    print(tasks)

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as e:
        print(e)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()


def stop():
    pass


class HydraProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        print("connection made")

    def connection_lost(self):
        print("connection lost")

    def datagram_received(self, data, addr):
        print("received data: ", data, "from ", addr)
        client_manager.handle_message(data)

    def error_received(self, exc):
        print("There was an error sending/receiving")
        print(exc)

    def pause_writing(self):
        print("The output buffer has been filled")

    def resume_writing(self):
        print("OS Signaled! Can now write to the buffer again")
