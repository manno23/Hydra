"""
  Networking

    Extends the event loop to add processing of a network msg buffer.
    - Describe pyglet event loop and how it is overridden

"""
import SocketServer
import socket
from threading import Thread
from Queue import Queue
from SocketServer import UDPServer
from pyglet import app
import sys

__author__ = 'manno23'


ADDRESS = ("192.168.1.2", 5555)


class NetworkExtendedEventLoop(app.EventLoop):
    def __init__(self):
        app.EventLoop.__init__(self)
        self.msg_queue = Queue()
        #We catch the error if the router is not plugged in
        self.server = MyServer(ADDRESS, UDPRequestHandler, self.msg_queue)
        self.t = Thread(target=self.server.serve_forever)
        self.t.daemon = True
        self.t.start()

    def idle(self):
        self.dispatch_event('on_midi_events_available')
        while not self.msg_queue.empty():
            self.dispatch_event('on_packets_available', self.msg_queue.get_nowait())
        return app.EventLoop.idle(self)
NetworkExtendedEventLoop.register_event_type('on_packets_available')
NetworkExtendedEventLoop.register_event_type('on_midi_events_available')


class UDPRequestHandler(SocketServer.ThreadingMixIn,SocketServer.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait((self.request, self.client_address))


class MyServer(UDPServer):
    def __init__(self, *args, **kwargs):
        """
        Will throw a socket error here if the address provided is not available.
        @param args:
        @param kwargs:
        @return:
        """
        try:
            UDPServer.__init__(self, *args, **kwargs)
        except socket.error:
            print 'Target router not connected'
            sys.exit()
        self.allow_reuse_address = True
        self.msg_queue = args[2]
