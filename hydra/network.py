import SocketServer
from threading import Thread
from Queue import Queue
from SocketServer import UDPServer
from pyglet import app
from pyglet.gl import *

__author__ = 'manno23'


class UDPRequestHandler(SocketServer.ThreadingMixIn,SocketServer.DatagramRequestHandler):
    def handle(self):
        self.server.msg_queue.put_nowait(self.request[0])


class MyServer(UDPServer):
    def __init__(self, *args, **kwargs):
        UDPServer.__init__(self, *args, **kwargs)
        self.msg_queue = args[2]


class NetworkExtendedEventLoop(app.EventLoop):
    def __init__(self, host):
        app.EventLoop.__init__(self)
        self.msg_queue = Queue()
        self.server = MyServer(host, UDPRequestHandler, self.msg_queue)
        self.t = Thread(target=self.server.serve_forever)
        self.t.daemon = True
        self.t.start()

    def idle(self):
        while not self.msg_queue.empty():
            self.dispatch_event('on_packets_available', self.msg_queue.get_nowait())
        return app.EventLoop.idle(self)

NetworkExtendedEventLoop.register_event_type('on_packets_available')


