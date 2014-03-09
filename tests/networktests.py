import socket
import unittest

import gevent
import pyglet

from hydra.hydra.network import NetworkExtendedEventLoop


__author__ = 'manno23'


class NetworkTest(unittest.TestCase):
    def setUp(self):
        print 'setup'
        self.number_of_clients = 5
        self.message_count = 100
        self.address = ("10.1.1.9", 5555)

        self.clients = []

        def client():
            count = 0
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while count < self.message_count:
                print 'client message', count
                sock.sendto(str(count), self.address)
                gevent.sleep()
                count += 1
            sock.sendto("stop", self.address)

        for _ in xrange(self.number_of_clients):
            self.clients.append(gevent.spawn(client))

        self.extended_loop = NetworkExtendedEventLoop(self.address)
        pyglet.app.event_loop = self.extended_loop

        @self.extended_loop.event
        def on_packets_available(data):
            print data

        pyglet.app.run()
        gevent.joinall(self.clients)
