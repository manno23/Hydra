import pyportmidi as midi
import socket as s
import struct

sock = s
sock = s.socket(s.AF_INET, s.SOCK_DGRAM)
midi.init()
msg = struct.pack('>HHHH', 1, 2, 3, 4)
ADDRESS = ('127.0.0.1', 5555)
