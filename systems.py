from mycolors import *
import time

# abstract system base class
class BasicSystem(object):
    def __init__(self, pg):
        self.pg = pg
        import components as cmps
        self.cmps = cmps


# Basically a key event listener
class HandlerSystem(BasicSystem):
    def __init__(self, pg):
        super(HandlerSystem, self).__init__(pg)
        # dict of key:f(): if 'key' ressed then run function f() on the player
        self.keyMap = {}

        # profiler variables
        self.keyProfilerNum = {}
        self.keyProfilerSpeed = {}
        self.speed_profiler = False

        # global keybinds don't have parameters
        # player specific have playerCtrl component as param

        def onEscape():
            return 'ext'
        self.addKey(pg.K_ESCAPE, onEscape)

        def onEnter():
            print("Enter pressed")
            return 'ent'
        self.addKey(pg.K_RETURN, onEnter)

        # pla - PLayer Action

        def plaStop(pl):
            pl.direction = 0
            return 'stp'

        def plaUp(pl):
            pl.direction = 1
            return 'mov'

        def plaRight(pl):
            pl.direction = 2
            return 'mov'

        def plaDown(pl):
            pl.direction = 3
            return 'mov'

        def plaLeft(pl):
            pl.direction = 4
            return 'mov'

        def plaDash(pl):
            print(pl.e.id + ": dash")
            return 'skl'

        def plaThrow(pl):
            print(pl.e.id + ": throw")
            return 'skl'

        # maps player's actions to correspondin functions
        self.actionMap = {
            'up': plaUp,
            'right': plaRight,
            'down': plaDown,
            'left': plaLeft,
            'dash': plaDash,
            'throw': plaThrow
        }

    # maps global key to keyMap
    def addKey(self, k, f):
        self.keyMap[k] = f
        self.keyProfilerNum[k] = 0
        self.keyProfilerSpeed[k] = []

    # if movement key wasn't pressed then stop player
    def reset(self, pl):
        pl.direction = 0

    # called in main loop
    def update(self, cmp_dict):
        res = 1

        keys = self.pg.key.get_pressed()

        # player keybinds
        for c in cmp_dict[self.cmps.PlayerCtrl]:
            total_mov = 0
            # go through custom player keybinds
            for actionstr, k in c.keyBinds.items():
                if keys[k]:
                    starttime = time.clock()  # for perfomance measure
                    ares = self.actionMap[actionstr](c)
                    if ares == 'mov': total_mov += 1
                    # profiler (perfomance measure stuff)
                    self.keyProfilerNum[k] += 1
                    if self.speed_profiler:
                        self.keyProfilerSpeed[k].append(time.clock() - starttime)
            # stop player if no movement was commanded
            if total_mov == 0: self.reset(c)

        # global keybinds
        for k, action in self.keyMap.items():
            if keys[k]:
                starttime = time.clock()
                # global keybinds define state of the app (like exit/pause)
                res = action()
                self.keyProfilerNum[k] += 1
                if self.speed_profiler:
                    self.keyProfilerSpeed[k].append(time.clock() - starttime)

        return res


class PhysicsSystem(BasicSystem):
    def __init__(self, pg):
        super(PhysicsSystem, self).__init__(pg)

        import components as cmps
        self.cmps = cmps

    def update(self, cmp_dict):
        for obj_type, comp_list in cmp_dict.items():
            for c in comp_list:
                pos = c.e.cmp_dict[self.cmps.Position]

                # Iterate through players phisics movement
                # BasicMovement component
                # if component has BasicMovement component and attached to a player
                if obj_type == self.cmps.BasicMovement and self.cmps.PlayerCtrl in c.e.cmp_dict:
                    direction = c.e.cmp_dict[self.cmps.PlayerCtrl].direction
                    if direction == 1:
                        pos.y -= c.speed
                    elif direction == 2:
                        pos.x += c.speed
                    elif direction == 3:
                        pos.y += c.speed
                    elif direction == 4:
                        pos.x -= c.speed

        return 1


class RenderSystem(BasicSystem):
    def __init__(self, pg, screen):
        super(RenderSystem, self).__init__(pg)
        self.screen = screen

        import components as cmps
        self.cmps = cmps

    def update(self, cmp_dict):
        # clear frame with background color
        self.screen.fill(BLACK)

        for _, comp_list in cmp_dict.items():
            for obj in comp_list:
                # no position - no render
                try: pos = obj.e.cmp_dict[self.cmps.Position]
                except KeyError: continue
                # render here
                obj.render_shape(self.screen, pos.x, pos.y)

        self.pg.display.flip()
        return 1