import gevent
from gevent.event import Event
from gevent import Greenlet, monkey

gevent.monkey.patch_sys()

class Green1(Greenlet):
    def __init__(self, running):
        self.running = running
        Greenlet.__init__(self)
    def _run(self):
        count1 = 0
        while self.running.is_set():
            count1 = count1 + 1
            gevent.sleep()
        print count1

class Green2(Greenlet):
    def __init__(self, running):
        self.running = running
        Greenlet.__init__(self)
    def _run(self):
        count2 = 0
        while self.running.is_set():
            count2 = count2 + 1
            gevent.sleep()
        print count2


class Controller(Greenlet):
    def __init__(self):
        self.running = gevent.event.Event()
        self.running.set()
        self.g1 = Green1(self.running)
        self.g2 = Green2(self.running)
        self.g1.start(); self.g2.start();
        Greenlet.__init__(self)

    def _run(self):
        print 'Started'
        gevent.joinall([self, self.g1,self.g2])
        while True:
            input = raw_input("$> ")
            if input == 'stop':
                self.running.clear()
                print 'Greenlets have ceased'
            elif input == 'begin' and not self.running.is_set():
                self.running.set()
                gevent.joinall([self, self.g1,self.g2])
                print 'restarted'
            elif input == 'exit':
                self.running.clear()
                print 'exiting'
                break
            else:
                print 'Usage: [stop/begin/exit]'
            gevent.sleep()



controller = Controller()
controller.start()
controller.join()

