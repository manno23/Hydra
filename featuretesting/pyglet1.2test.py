__author__ = 'jason'

import os, threading
from numpy import asbytes

class Device(object):
    def __init__(self):
        self._sync_file_read, self._sync_file_write = os.pipe()
        self._event = threading.Event()

    def fileno(self):
        return self._sync_file_read

    def set(self):
        self._event.set()
        os.write(self._sync_file_write, asbytes('1'))

    def select(self):
        self._event.clear()
        os.read(self._sync_file_read, 1)

    def poll(self):
        return self._event.isSet()

# timeout is determined by a prediction algorithm
def step(self, timeout=None):
    device = Device()
    select_devices = set()
    select_devices.add(device)

    pending_devices = []
    for d in select_devices:
        if d.poll():
            pending_devices.append(d)

    if not pending_devices and (timeout is None or timeout > 0.0):
        iwtd = select_devices
        pending_devices = select.select(iwtd, (), (), timeout)

    if not pending_devices:
        return False
