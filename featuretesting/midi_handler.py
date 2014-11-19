import asyncio
from pyportmidi import Input, Output, init

init()

@asyncio.coroutine
def check_midi_port(port_id):
    o = Input(port_id)
    yield from o.read(64)

'''
Where is the expensive IO?
What classifies as an IO? Use of an asynchronous system call? select, poll
Are midi reads or writes considered IO?

Windows is using IOCP


Yield on blocking io calls
Swap between
    midi_data = Check Midi Buffers Non-Blocking
    network_data = Check Socket Connections Blocking
    Connection_manager(midi_data, network_data)
        ---> Processes this to update the Scene State
                This then sends midi to ports 
                sends network messages to clients -> Blocking
'''

