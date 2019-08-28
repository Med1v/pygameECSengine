import pygame
from systems import *

class Component(object):
    def __init__(self, systems):
        # each component has list of system types that must work on component
        # and link to entity to perform component interaction
        self.systems = systems
        self.e = None


class Transform(Component):
    def __init__(self, posx, posy):
        super().__init__([])
        self.x = posx
        self.y = posy
        self.a = 0  # ?


class BasicMovement(Component):
    def __init__(self, speed):
        super().__init__([PhysicsSystem])
        self.speed = speed


class InertiaMovement(Component):
    def __init__(self, friction, power, weight, maxspeed, speedx=0, speedy=0):
        super().__init__([PhysicsSystem])
        self.friction = friction
        self.weight = weight
        self.power = power
        self.forces = [0, 0, 0, 0]  # up; right; down; left
        self.speedx = speedx
        self.speedy = speedy
        self.maxspeed = maxspeed  # ?


class CollisionBox(Component):
    def __init__(self, width, height):
        super().__init__([PhysicsSystem])
        self.width = width
        self.height = height


class PlayerCtrl(Component):
    def __init__(self, keyBindsMap):
        super().__init__([HandlerSystem, BotSystem])
        # up; right; down; left
        self.keyBinds = keyBindsMap
        self.direction = [0, 0, 0, 0]


class ChaseBotCtrl(Component):
    def __init__(self):
        super().__init__([BotSystem])
        # up; right; down; left
        self.direction = [0, 0, 0, 0]


class Rectangle(Component):
    def __init__(self, color, size):
        super().__init__([RenderSystem])
        self.color = color
        self.size = size
        self.render_shape = lambda s, x, y: pygame.draw.rect(s, self.color, pygame.Rect(x, y, self.size, self.size))