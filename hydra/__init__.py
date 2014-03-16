import struct
from pygame import midi
from hydra.graphics import *
from hydra.midihandler import MidiHandler
from hydra.network import *


__author__ = 'manno23'

ADDRESS = ("10.1.1.7", 5555)
initial_matrix = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
rot_matrix = (gl.GLfloat * 16)(*initial_matrix)


def run_server():
    extended_loop = NetworkExtendedEventLoop(ADDRESS)
    midi_handler = MidiHandler()
    pyglet.app.event_loop = extended_loop
    window = pyglet.window.Window(resizable=True)

    # Setup OpenGL scene
    glClearColor(1, 1, 1, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # Define a simple function to create ctypes arrays of floats:
    def vec(*args):
        return (GLfloat * len(args))(*args)

    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, vec(0.5, 0, 0.3, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vec(1, 1, 1, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
    rect = Rectangle(2, 4, 1)

    @extended_loop.event
    def on_packets_available(data):
        global rot_matrix
        if type == 1.0:
            out = struct.unpack('!ff', data)[1]
            midi_handler.handle(type, out=out)
        elif type == 2.0:
            out = struct.unpack('!fffffffffffffffff', data)[1:]
            rot_matrix = (gl.GLfloat * len(out))(*out)
            x, y, z = rot_mat_to_angle(rot_matrix)
            midi_handler.handle(type, x=x, y=y, z=z)




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