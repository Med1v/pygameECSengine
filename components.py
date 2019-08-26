from systems import *

class Component(object):
    def __init__(self, systems):
        self.systems = systems


class Position(Component):
    def __init__(self, posx, posy):
        super(PlayerCtrl, self).__init__([HandlerSystem, RenderSystem])
        # 0-no; 1-up; 2-right; 3-down; 4-left
        self.pos.x = posx
        self.pos.y = posy


class PlayerCtrl(Component):
    def __init__(self, posx, posy):
        super(PlayerCtrl, self).__init__([HandlerSystem])
        # 0-no; 1-up; 2-right; 3-down; 4-left
        self.pos.x = posx
        self.pos.y = posy
        self.direction = 0


class Rectangle(Component):
    def __init__(self, posx, posy, color, size):
        super(PlayerCtrl, self).__init__([RenderSystem])
        self.color = color
        self.size = size