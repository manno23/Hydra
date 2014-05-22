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

    graphics_handler = GraphicsHandler()
    client_manager = ClientManager(graphics_handler)
    extended_loop = NetworkExtendedEventLoop()

    pyglet.app.event_loop = extended_loop
    window = pyglet.window.Window(resizable=True)



    @extended_loop.event
    def on_packets_available(packet):
        client_manager.handle_message(packet)


    @extended_loop.event
    def poll_midi_events():
        client_manager.poll_midi_events()


    @window.event
    def on_resize(width, height):
        graphics_handler.on_resize(width, height)
        return pyglet.event.EVENT_HANDLED

    def update(rt):
        pass
    pyglet.clock.schedule(update)

    @window.event
    def on_draw():
        graphics_handler.on_draw()

    pyglet.app.run()

if __name__ == "__main__":
    run_server()