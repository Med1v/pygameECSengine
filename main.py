import pygame
# from event_manager import EventManager

from systems import *
from components import *
import entity

swidths, sheight = 800, 800
FPS_LIMIT = 120


class ECManger(object):
    def __init__(self):
        self.sys_list = {}
        self.cmp_list = {}

    def addSys(self, s):
        self.sys_list[type(s)] = s
        self.cmp_list[type(s)] = {}

    def newEC(self, c):
        for s in c.systems:
            # if current componen list for system s doesn't exist: create it
            try: self.cmp_list[s][type(c)]
            except KeyError: self.cmp_list[s][type(c)] = []
            self.cmp_list[s][type(c)].append(c)
            # init unique components
            if (type(c) == PlayerCtrl):
                self.sys_list[HandlerSystem].initPlayerKeyBinds(c)


def run():
    screen = pygame.display.set_mode([swidths, sheight])
    pygame.display.set_caption("untittled game")

    ecsmng = ECManger()

    ecsmng.addSys(HandlerSystem(pygame))
    ecsmng.addSys(PhysicsSystem(pygame))
    ecsmng.addSys(RenderSystem(pygame, screen))
    # init entities
    entity.init(ecsmng)

    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # System update section
        sysres = []
        for stype, s in ecsmng.sys_list.items():
            sysres.append(s.update(ecsmng.cmp_list[stype]))

        if 'ext' in sysres: game_over = True

        pygame.time.Clock().tick(FPS_LIMIT)

    pygame.quit()


if __name__ == '__main__':
    pygame.init()
    print("init ran")
    run()