from pyglet import graphics, gl

__author__ = 'jason'


class Rectangle(object):
    def __init__(self, width, height, depth):
        # Create the vertex arrays
        left_face_vertices = [-width / 2., -height / 2., -depth / 2.,
                              -width / 2., height / 2., -depth / 2.,
                              -width / 2., height / 2., depth / 2.,
                              -width / 2., -height / 2., depth / 2.]
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