import pygame
from components import *
from systems import *
from mycolors import *

class Entity(object):
    def __init__(self, eid, manager):
        self.id = eid
        self.manager = manager
        self.cmp_dict = {}

    def addComponent(self, c):
        self.cmp_dict[type(c)] = c
        c.e = self
        self.manager.newEC(c)


def init(mng):
    elist = []

    player1 = Entity('player1', mng)
    keyBinds = {
        'up': pygame.K_w,
        'right': pygame.K_d,
        'down': pygame.K_s,
        'left': pygame.K_a,
        'dash': pygame.K_v,
        'throw': pygame.K_b
    }
    player1.addComponent(PlayerCtrl(keyBinds))
    player1.addComponent(Position(100, 100))
    player1.addComponent(BasicMovement(5))
    player1.addComponent(Rectangle(BLUE, 50))

    elist.append(player1)

    player2 = Entity('player2', mng)
    keyBinds = {
        'up': pygame.K_UP,
        'right': pygame.K_RIGHT,
        'down': pygame.K_DOWN,
        'left': pygame.K_LEFT,
        'dash': pygame.K_p,
        'throw': pygame.K_o
    }
    player2.addComponent(PlayerCtrl(keyBinds))
    player2.addComponent(Position(300, 300))
    player2.addComponent(BasicMovement(5))
    player2.addComponent(Rectangle(RED, 50))

    elist.append(player2)

    return elist