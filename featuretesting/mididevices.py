__author__ = 'Jason Manning'
import gevent
from gevent import server

available_devices = list()

def main():
    HOST, PORT = 'localhost', 5555
    server = MyUDPServer((HOST, PORT))
    server.serve_forever()

class MyUDPServer(gevent.server.DatagramServer):
    def handle(self):
        data = self.request[0].strip()
        print ">> (" + self.client_address[0] + ")"
        print data

if __name__ == "__main__":
    main()
