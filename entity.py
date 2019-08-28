import pygame
from components import *
from systems import *
from mycolors import *

class Entity(object):
    def __init__(self, eid, manager):
        # each entity has unique name (id) link to system/component manager
        # and dict of components for components interaction
        self.id = eid
        self.manager = manager
        self.cmp_dict = {}

    def addComponent(self, c):
        # assign local variables and pass it to manager
        self.cmp_dict[type(c)] = c
        c.e = self
        self.manager.newEC(c)


def init(mng):
    PLAYER_FRICTION = 20

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
    player1.addComponent(Transform(200, 200))
    # friction, power, weight, maxspeed, speedx=0, speedy=0
    player1.addComponent(InertiaMovement(PLAYER_FRICTION, 30, 25, 10))
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
    player2.addComponent(Transform(200, 400))
    # player2.addComponent(BasicMovement(5))
    # friction, power, weight, maxspeed, speedx=0, speedy=0
    player2.addComponent(InertiaMovement(PLAYER_FRICTION, 30, 25, 10))
    player2.addComponent(Rectangle(WHITE, 50))

    elist.append(player2)

    bot1 = Entity('bot1', mng)
    bot1.addComponent(ChaseBotCtrl())
    bot1.addComponent(Transform(500, 400))
    bot1.addComponent(InertiaMovement(PLAYER_FRICTION*2, 30, 150, 10))
    bot1.addComponent(Rectangle(RED, 50))

    return elist