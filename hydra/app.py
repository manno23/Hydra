'''
 HydraServer

    Need to seperate concerns of user interface and midi server.
    Manages phone clients, allowing the sending/receiving of midi messages

    TODO:
    * Add Logging
    * Allow user to configure router or have it done automatically
        - map out the range of possibilites (not plugged in, etc...)
    * Add gui

'''
import sys
import asyncio
import threading
import socketserver
import pyportmidi

from . import client_manager


ADDRESS = ("localhost", 5555)


def run():

    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()

    pyportmidi.init()

    def tha_loop():

        cm = client_manager.ClientManager()
        print('entering tha loop')

        while True:

            # Get items off the queue
            for _ in range(32):
                try:
                    cm.handle_message(msg_queue.get_nowait())
                except:
                    break

            cm.handle_midi()

            asyncio.sleep(0.00001)

    task = asyncio.async(tha_loop())
    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass


def close():
    loop.close()
    server.close()
    pass


class UDPRequestHandler(socketserver.ThreadingMixIn,
                        socketserver.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait((self.request, self.client_address))


class MyServer(socketserver.UDPServer):
    def __init__(self, *args, **kwargs):
        try:
            socketserver.UDPServer.__init__(self, *args, **kwargs)
        except Exception as e:
            print(e)
            print ('Target router not connected')
            sys.exit()
        self.allow_reuse_address = True
        self.msg_queue = args[2]

loop = asyncio.get_event_loop()
msg_queue = asyncio.queues.Queue()
server = MyServer(ADDRESS, UDPRequestHandler, msg_queue)
