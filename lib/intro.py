# -*- encoding: utf-8 -*-
from cocos.actions import *
from scene import Scene
import common

class Intro(Scene):

    def __init__(self, world):
        Scene.__init__(self, world)
        self.change_subscene(SubScene1(self))

    def change_subscene(self, scene):
        self.sub_scene = scene
        self.step = 0

    def update(self, dt):
        self.step += dt

        if self.step > 4:
            self.sub_scene.next()
            self.step = 0

    def on_draw(self):
        self.sub_scene.on_draw()

    def on_key_press(self, symbol, state):
        if common.is_continue_key(symbol):
            self.skip_scene()

    def skip_scene(self):
        import game
        self.world.change_scene(game.Game(self.world))


class SubScene:
    def __init__(self, father):
        self.father = father
        self.layer = common.load_image('layer.png')

class SubScene1(SubScene):

    def __init__(self, father):
        SubScene.__init__(self, father)
        self._create_sprites()
        # TODO: se repite varias veces, se prodría transladar a una clase padre.

    def _create_sprites(self):
        sky = ActionSprite(common.load_image('intro/sky2.png'))
        sky.y = 118
        sky.do(Move((-100, 0), 6))

        intro_1 = ActionSprite(common.load_image('intro/intro_1.png'))
        intro_1.x = 95
        intro_1.y = 118
        intro_1.scale = 1.2
        intro_1.do(Scale(1.1, 6))

        run = ActionSprite(common.load_image('intro/run.png'))
        run.x = 400
        run.y = 80
        run.do(Scale(1.1, 6))

        self.sprites = [sky, intro_1, run]

    def on_draw(self):
        for s in self.sprites[:-1]:
            s.draw()

        self.layer.blit(0, 0)
        self.sprites[-1].draw()

    def next(self):
        self.father.change_subscene(SubScene2(self.father))


class SubScene2(SubScene):

    def __init__(self, father):
        SubScene.__init__(self, father)
        self._create_sprites()

    def _create_sprites(self):
        sky = ActionSprite(common.load_image('intro/sky2.png'))
        sky.y = 118
        sky.x = 100
        sky.do(Move((-200, 0), 6))

        intro_1 = ActionSprite(common.load_image('intro/front.png'))
        intro_1.x = 120
        intro_1.y = 100
        intro_1.scale = 1.2

        run = ActionSprite(common.load_image('intro/rat.png'))
        run.x = -500
        run.y = 90
        run.scale = 1.5
        run.do(Jump(10, 300, 10, 0.4) + Delay(1.5) + Jump(10, 700, 10, 0.4))

        self.sprites = [sky, intro_1, run]

    def update(self, dt):
        pass

    def on_draw(self):
        for s in self.sprites:
            s.draw()

        self.layer.blit(0, 0)

    def next(self):
        self.father.change_subscene(SubScene3(self.father))

class SubScene3(SubScene):

    def __init__(self, father):
        SubScene.__init__(self, father)
        self._create_sprites()

    def _create_sprites(self):
        pass

    def update(self, dt):
        pass

    def on_draw(self):
        pass

    def next(self):
        pass