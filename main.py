import pygame
# from event_manager import EventManager

from systems import *
from components import *
import entity

swidths, sheight = 1700, 800
FPS_LIMIT = 15


class ECManger(object):
    def __init__(self):
        self.sys_list = {}
        self.cmp_list = {}

    def addSys(self, s):
        # dict of systems
        self.sys_list[type(s)] = s
        # dict of dicts of list of components
        self.cmp_list[type(s)] = {}

    def newEC(self, c):
        for s in c.systems:
            # if current componen list for system 's' doesn't exist: create it
            try: self.cmp_list[s][type(c)]
            except KeyError: self.cmp_list[s][type(c)] = []
            # add component to the dicts of list
            self.cmp_list[s][type(c)].append(c)


def run():
    screen = pygame.display.set_mode([swidths, sheight])
    pygame.display.set_caption("untitled game")

    # initiate component/system manager and add systems to queue
    ecsmng = ECManger()

    ecsmng.addSys(HandlerSystem(pygame))
    ecsmng.addSys(BotSystem(pygame))
    ecsmng.addSys(CollisionSystem(pygame, [swidths, sheight]))
    ecsmng.addSys(PhysicsSystem(pygame))
    ecsmng.addSys(RenderSystem(pygame, screen))
    # init entities and add components to them
    entity.init(ecsmng)

    # main game loop
    game_over = False
    while not game_over:
        # on pressing x on the top let of the window or alt+f4
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # System update section. Do 1 frame update for each system
        # with proper components
        sysres = []
        for stype, s in ecsmng.sys_list.items():
            sysres.append(s.update(ecsmng.cmp_list[stype]))

        # if at least 1 of the systems called on exit then stop main loop
        if 'ext' in sysres: game_over = True
        # fps limiter
        # pygame.time.Clock().tick(FPS_LIMIT)

    pygame.quit()


if __name__ == '__main__':
    pygame.init()
    print("init ran")
    run()