import pygame
from systems import *

class Component(object):
    def __init__(self, systems):
        self.systems = systems
        self.e = None


class Position(Component):
    def __init__(self, posx, posy):
        super().__init__([])
        self.x = posx
        self.y = posy


class BasicMovement(Component):
    def __init__(self, speed):
        super().__init__([PhysicsSystem])
        self.speed = speed


class PlayerCtrl(Component):
    def __init__(self, keyBindsMap):
        super().__init__([HandlerSystem])
        # 0-no; 1-up; 2-right; 3-down; 4-left
        self.keyBinds = keyBindsMap
        self.direction = 0


class Rectangle(Component):
    def __init__(self, color, size):
        super().__init__([RenderSystem])
        self.color = color
        self.size = size
        self.render_shape = lambda s, x, y: pygame.draw.rect(s, self.color, pygame.Rect(x, y, self.size, self.size))