import struct
import pyglet
from pyglet.gl import *
from hydra.graphics import Rectangle
from hydra.network import NetworkExtendedEventLoop


__author__ = 'manno23'

ADDRESS = ("10.1.1.9", 5555)
initial_matrix = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
rot_matrix = (gl.GLfloat * 16)(*initial_matrix)

def run_server():
    extended_loop = NetworkExtendedEventLoop(ADDRESS)
    pyglet.app.event_loop = extended_loop
    window = pyglet.window.Window(resizable=True)

    rect = Rectangle(2, 4, 1)

    @extended_loop.event
    def on_packets_available(data):
        global rot_matrix
        if len(data) is 17 * 4:
            out = struct.unpack('!fffffffffffffffff', data)[1:]
            rot_matrix = (gl.GLfloat * len(out))(*out)

    @window.event
    def on_resize(width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., width / float(height), .1, 1000.)
        glTranslatef(0.0, 0.0, -12.0)
        glMatrixMode(GL_MODELVIEW)
        return pyglet.event.EVENT_HANDLED

    def update(rt):
        pass
    pyglet.clock.schedule(update)

    @window.event
    def on_draw():
        global rot_matrix
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glMultMatrixf(rot_matrix)
        rect.draw()

    pyglet.app.run()

if __name__ == "__main__":
    run_server()