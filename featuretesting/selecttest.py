__author__ = 'Jason'

from gevent import socket
import socket
from gevent import select

# what file descriptors are available as python objects?
# sockets, files
# on windows only sockets are available
ADDRESS = ('localhost', 2323)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(ADDRESS)
sock.recvfrom(64)

tuple = select.select([sock],[],[])
for i in tuple:
    print i
