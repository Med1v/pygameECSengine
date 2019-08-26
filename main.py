import pygame
from mycolors import *
# from event_manager import EventManager

from systems import *

swidths, sheight = 800, 800
FPS_LIMIT = 120


class ECManger(object):
    def __init__(self):
        self.sys_list = {}

    def addSys(self, s):
        self.sys_list[type(s)] = s

    def newEC(e, c):
        pass


def run():
    ecsmng = ECManger()

    ecsmng.addSys(RenderSystem(pygame))
    ecsmng.addSys(HandlerSystem(pygame))

    game_over = False
    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        # System update section
        sysres = []
        for _, s in ecsmng.sys_list.items():
            sysres.append(s.update())

        if min(sysres) <= 0: game_over = True

        pygame.time.Clock().tick(FPS_LIMIT)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    pygame.init()
    print("init ran")
    screen = pygame.display.set_mode([swidths, sheight])
    pygame.display.set_caption("untittled game")
    screen.fill(BLACK)
    run()