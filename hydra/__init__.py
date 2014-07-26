'''
 HydraServer

    Manages phone clients, allowing the sending/receiving of midi messages

'''
import pyglet
from pyglet.gl import *
from hydra.client_manager import ClientManager

from hydra.graphics import GraphicsHandler
from hydra.midihandler import MidiHandler
from hydra.network import *

__author__ = 'manno23'


def run_server():

    gh = GraphicsHandler()
    cm = ClientManager(gh)
    extended_loop = NetworkExtendedEventLoop()

    pyglet.app.event_loop = extended_loop
    window = pyglet.window.Window(resizable=True)

    @extended_loop.event
    def on_packets_available(packet):
        cm.handle_message(packet)

    @extended_loop.event
    def on_midi_events_available():
        cm.handle_midi()

    @window.event
    def on_resize(width, height):
        gh.on_resize(width, height)
        return pyglet.event.EVENT_HANDLED

    def update(rt):
        pass
    pyglet.clock.schedule(update)

    @window.event
    def on_draw():
        gh.on_draw()

    pyglet.app.run()

if __name__ == "__main__":
    run_server()