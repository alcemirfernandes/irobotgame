# -*- encoding: utf-8 -*-
# I Robot? - a dancing robot game for pyweek
#
# Copyright: 2008 Hugo Ruscitti
# License: GPL 3
# Web: http://www.losersjuegos.com.ar

import sys

import pyglet

import text
from scene import Scene
from cocos.actions import *
import random
import common


def show_name(action, (name, text)):
    persons = {
        'hugoruscitti': ('Hugo Ruscitti', 'Programming', 320, 330),
        'cristian': ('Cristian Villalba', 'Programming and musics', 290, 230),
        'walter': ('Walter Velazquez', 'Art', 320, 350),
        'javi': ('Javier Da Silva', 'Art', 280, 340),
        }

    fullname, task, x, y = persons[name]
    text.set_text(fullname, task)
    text.set_position(x, y)


def hide_text(action, text):
    text.set_text('', '')

class About(Scene):
    
    def __init__(self, world):
        Scene.__init__(self, world)
        self.step = 0
        self._load_background()
        self.name = text.AboutText()
        self._create_sprites()

        pyglet.clock.schedule_once(self.show_losersjuegos_logo, 4 + 3 * 2)

    def init(self):
        for index, sprite in enumerate(self.sprites):
            name = sprite.name
            image = sprite.image_copy
            SPEED = 0.5
            sprite.do(Delay(index * 2) + Delay(1) +  
                    (FadeIn(SPEED) | Move((0, image.height), SPEED)) +
                    CallFuncS(show_name, (name, self.name)) + 
                    Delay(1) + CallFuncS(hide_text, self.name) + 
                    (Scale(0.3, 1) | Move((350 - index * 70, 0), 1)))



    def show_losersjuegos_logo(self, dt):
        images = [
                common.load_image('presents/frame_1.png'),
                common.load_image('presents/frame_2.png'),
                ]

        animation = pyglet.image.Animation.from_image_sequence(images, 0.10)
        
        self.logo = ActionSprite(animation)
        self.logo.opacity = 0
        self.logo.x = 0
        self.logo.y = 0
        self.logo.do(FadeIn(2))
        self.sprites.insert(0, self.logo)
        self.name.set_text('Thanks !', 'http://www.losersjuegos.com.ar')
        self.name.set_position(180, 400)

    def _load_background(self):
        images = [
                common.load_image('about/1.png'),
                common.load_image('about/2.png'),
                ]

        animation = pyglet.image.Animation.from_image_sequence(images, 0.10)
        self.animation = ActionSprite(animation)
        self.animation.x = 0
        self.animation.y = 0

    def hide_text(self, dt):
        self.name.set_text('', '')

    def _create_sprites(self):
        self.names = ['hugoruscitti', 'walter', 'cristian', 'javi']
        self.sprites = []

        for index, name in enumerate(self.names):
            image = common.load_image('about/%s.png' %name)
            sprite = ActionSprite(image)
            sprite.x = 50
            sprite.y = - image.height
            sprite.image_copy = image
            sprite.name = name
            sprite.opacity = 0

            self.sprites.append(sprite)


    def update(self, dt):
        self.step += dt

        if self.step > 17:
            import sys
            sys.exit(0)

    def on_draw(self):
        self.animation.draw()

        for sprite in self.sprites:
            sprite.draw()

        self.name.draw()

    def _exit(self):
        sys.exit(0)

    def on_mouse_press(self, x, y, bottom, extra=None):
        self._exit()

    def on_key_press(self, symbol, extra):
        if common.is_continue_key(symbol):
            self._exit()
        elif symbol == pyglet.window.key.ESCAPE:
            self._exit()

    def destroy(self):
        self.animation.stop()

        try:
            self.logo.stop()
        except AttributeError:
            pass

        for sprite in self.sprites:
            sprite.stop()

if __name__ == '__main__':
    import test_about
