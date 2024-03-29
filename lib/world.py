# -*- encoding: utf-8 -*-
# I Robot? - a dancing robot game for pyweek
#
# Copyright: 2008 Hugo Ruscitti
# License: GPL 3
# Web: http://www.losersjuegos.com.ar

import sys
import gc

import pyglet
from pyglet.gl import *

import common
import config
import game
import audio
import presents


class World(pyglet.window.Window):

    def __init__(self, start_scene=True):
        pyglet.window.Window.__init__(self, caption='I Robot ?', 
                resizable=True, vsync=config.VSYNC)
        self.audio = audio.Audio()
        self._set_icons()
        self._scene = None
        self.enable_alpha_blending()
        self._init_window_size()

        if config.DEBUG:
            self.fps = pyglet.clock.ClockDisplay()
        else:
            self.fps = None

        if config.MOVE_WINDOW:
            self.set_location(400, 400)

        if config.FULLSCREEN:
            self.set_fullscreen()

        pyglet.clock.schedule_interval(self.update, 1/60.0)
        self._new_scene = None

        if start_scene:
            if config.DEBUG:
                import post_game_scenes
                new_scene = post_game_scenes.Final(self, None)
                self.change_scene(new_scene)
            else:
                import presents
                self.change_scene(presents.Presents(self))

    def run(self):
        pyglet.app.run()

    def _set_icons(self):
        icons = ['16', '32', '64', '128']
        names = ["icons/%s.png" %(n) for n in icons]
        images = [common.load_image(name) for name in names]
        self.set_icon(*images)

    def change_scene(self, scene):
        self._new_scene = scene

    def _do_change_scene(self):
        if self._scene:
            self.pop_handlers()
            self._scene.destroy()

        self._scene = self._new_scene
        self.push_handlers(self._scene)
        self._new_scene = None
        gc.collect()


    def on_draw(self):
        if config.DEBUG:
            self.fps.draw()

    def update(self, dt):
        self.audio.update()

        if self._new_scene:
            self._do_change_scene()
            self._scene.init()

        self._scene.update(dt)

    def on_key_press(self, symbol, extra):
        if symbol == pyglet.window.key.F:
            self.set_fullscreen(not self.fullscreen)
            self.capture_mouse()
        elif symbol == pyglet.window.key.Q:
            # The boss key handler
            # o como decimos en el barrio: pa' que el jefe no te descubra jugando...
            sys.exit(0)
        elif symbol == pyglet.window.key.S:
            from about import About as Scene
            new_scene = Scene(self)
            self.change_scene(new_scene)


    def capture_mouse(self):
        self.set_exclusive_mouse(True)
        self.set_mouse_visible(False)


    # TODO: Llevar estas rutinas a otra clase abstracta, o extender "cocos.director".
    def _init_window_size(self):
        self._window_original_width = self.width
        self._window_original_height = self.height
        self._window_aspect =  self.width / float( self.height )
        self._offset_x = 0
        self._offset_y = 0

    def get_virtual_coordinates( self, x, y ):
        """Transforms coordinates that belongs the *real* window size, to the
        coordinates that belongs to the *virtual* window.

        For example, if you created a window of 640x480, and it was resized
        to 640x1000, then if you move your mouse over that window,
        it will return the coordinates that belongs to the newly resized window.
        Probably you are not interested in those coordinates, but in the coordinates
        that belongs to your *virtual* window. 

        :rtype: (x,y)           
        :returns: Transformed coordinates from the *real* window to the *virtual* window
        """

        x_diff = self._window_original_width / float( self.window.width - self._offset_x * 2 )
        y_diff = self._window_original_height / float( self.window.height - self._offset_y * 2 )

        adjust_x = (self.window.width * x_diff - self._window_original_width ) / 2
        adjust_y = (self.window.height * y_diff - self._window_original_height ) / 2

        return ( int( x_diff * x) - adjust_x,   int( y_diff * y ) - adjust_y )


    def on_resize( self, width, height):
        """Method that is called every time the main window is resized.
        
        :Parameters:
            `width` : Integer
                New width
            `height` : Integer
                New height
        """
        width_aspect = width
        height_aspect = int( width / self._window_aspect)

        if height_aspect > height:
            width_aspect = int( height * self._window_aspect )
            height_aspect = height

        self._offset_x = (width - width_aspect) / 2
        self._offset_y =  (height - height_aspect) / 2

        glViewport(self._offset_x, self._offset_y, width_aspect, height_aspect )
        glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self._window_original_width, 0, self._window_original_height, -1, 1)
        glMatrixMode(gl.GL_MODELVIEW)

        
    #
    # Misc functions
    #
    def enable_alpha_blending( self ):
        """Enables alpha blending in OpenGL using the GL_ONE_MINUS_SRC_ALPHA algorithm."""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

