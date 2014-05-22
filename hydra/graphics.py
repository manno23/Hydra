import math
from pyglet import graphics, gl
from pyglet.gl import *
import struct

__author__ = 'jason'


class GraphicsHandler:
    def __init__(self):

        self.initial_matrix = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        self.rot_matrix = (gl.GLfloat * 16)(* self.initial_matrix)
        self.rect = Rectangle(2, 4, 1)

         # Setup OpenGL scene
        glClearColor(1, 1, 1, 1)
        glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, self.vec(0.5, 0, 0.3, 1))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.vec(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., width / float(height), .1, 1000.)
        glTranslatef(0.0, 0.0, -12.0)
        glMatrixMode(GL_MODELVIEW)

    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glMultMatrixf(self.rot_matrix)
        self.rect.draw()

    def on_packets_available(self, id, type, data):
        if type is 5: #Scene output
            out = struct.unpack('!ffffffffffffffff', data)
            self.rot_matrix = (gl.GLfloat * len(out))(*out)

    def vec(self, *args):
        return (GLfloat * len(args))(*args)


class Rectangle(object):
    def __init__(self, width, height, depth):
        # Create the vertex arrays
        left_face_vertices = [-width / 2., -height / 2., -depth / 2.,
                              -width / 2., -height / 2., depth / 2.,
                              -width / 2., height / 2., depth / 2.,
                              -width / 2., height / 2., -depth / 2.]
        front_face_vertices = [-width / 2., -height / 2., depth / 2.,
                               width / 2., -height / 2., depth / 2.,
                               width / 2., height / 2., depth / 2.,
                               -width / 2., height / 2., depth / 2.]
        right_face_vertices = [width / 2., -height / 2., depth / 2.,
                               width / 2., -height / 2., -depth / 2.,
                               width / 2., height / 2., -depth / 2.,
                               width / 2., height / 2., depth / 2.]
        back_face_vertices = [width / 2., -height / 2., -depth / 2.,
                              -width / 2., -height / 2., -depth / 2.,
                              -width / 2., height / 2., -depth / 2.,
                              width / 2., height / 2., -depth / 2.]
        top_face_vertices = [-width / 2., height / 2., depth / 2.,
                             width / 2., height / 2., depth / 2.,
                             width / 2., height / 2., -depth / 2.,
                             -width / 2., height / 2., -depth / 2.]
        bottom_face_vertices = [-width / 2., -height / 2., -depth / 2.,
                                width / 2., -height / 2., -depth / 2.,
                                width / 2., -height / 2., depth / 2.,
                                -width / 2., -height / 2., depth / 2.]

        self.vertex_list1 = graphics.vertex_list(4, ('v3f', left_face_vertices),
                                                 ('c3B', [255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0]))
        self.vertex_list2 = graphics.vertex_list(4, ('v3f', front_face_vertices),
                                                 ('c3B', [0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255]))
        self.vertex_list3 = graphics.vertex_list(4, ('v3f', right_face_vertices),
                                                 ('c3B', [0, 255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0]))
        self.vertex_list4 = graphics.vertex_list(4, ('v3f', back_face_vertices),
                                                 ('c3B', [255, 255, 0, 255, 255, 0, 255, 255, 0, 255, 255, 0]))
        self.vertex_list5 = graphics.vertex_list(4, ('v3f', top_face_vertices),
                                                 ('c3B', [255, 0, 255, 255, 0, 255, 255, 0, 255, 255, 0, 255]))
        self.vertex_list6 = graphics.vertex_list(4, ('v3f', bottom_face_vertices),
                                                 ('c3B', [0, 255, 255, 0, 255, 255, 0, 255, 255, 0, 255, 255]))

    def draw(self):
        self.vertex_list1.draw(gl.GL_QUADS)
        self.vertex_list2.draw(gl.GL_QUADS)
        self.vertex_list3.draw(gl.GL_QUADS)
        self.vertex_list4.draw(gl.GL_QUADS)
        self.vertex_list5.draw(gl.GL_QUADS)
        self.vertex_list6.draw(gl.GL_QUADS)


def rot_mat_to_angle(R):
    x = math.atan2(R[1], R[5]) * 180/math.pi
    y = math.asin(-R[9]) * 180/math.pi
    z = math.atan2(R[8], R[10]) * 180/math.pi
    return x, y, z