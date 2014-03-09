import threading

class SharedMemory:
    def __init__(self):
        self.mutex = threading.Lock()
        self.value = 0

    def set_value(self, value):
        self.mutex.acquire()
        self.value = value
        self.mutex.release()

    def read_value(self):
        self.mutex.acquire()
        out = self.value
        self.mutex.release()
        return out


class NetworkThread(threading.Thread):
    def __init__(self, sm):
        sm.set_value(12)

    def setvalue(self, value):
        sm.set_value(value)


class RenderThread(threading.Thread):
    def __init__(self, sm):
        print sm.read_value()

    def readvalue(self):
        return sm.read_value()

sm = SharedMemory()
n = NetworkThread(sm)
r = RenderThread(sm)

n.setvalue(18)
print r.readvalue()
