from mycolors import *
import time


class BasicSystem(object):
    def __init__(self, pg):
        self.pg = pg
        self.cemap = {}
        import components as cmps
        self.cmps = cmps

    def addComponent(self, cmp, ent):
        self.cemap[cmp] = ent


class HandlerSystem(BasicSystem):
    def __init__(self, pg):
        super(HandlerSystem, self).__init__(pg)
        self.keyMap = {}
        self.keyProfilerNum = {}
        self.keyProfilerSpeed = {}
        self.speed_profiler = False

        def onEscape():
            return 'ext'
        self.addKey(pg.K_ESCAPE, onEscape)

        def onEnter():
            print("Enter pressed")
            return 'ent'
        self.addKey(pg.K_RETURN, onEnter)

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

        self.actionMap = {
            'up': plaUp,
            'right': plaRight,
            'down': plaDown,
            'left': plaLeft,
            'dash': plaDash,
            'throw': plaThrow
        }

    def initPlayerKeyBinds(self, c):
        print("binding this player controls:")
        print(c.keyBinds)
        # for action, key in c.keyBinds.items():
        #     self.addKey(key, self.actionMap[action])

    def addKey(self, k, f):
        self.keyMap[k] = f
        self.keyProfilerNum[k] = 0
        self.keyProfilerSpeed[k] = []

    def reset(self, pl):
        pl.direction = 0
        # print(f"reset called")

    def update(self, cmp_dict):
        res = 1

        keys = self.pg.key.get_pressed()

        # player keybinds
        for c in cmp_dict[self.cmps.PlayerCtrl]:
            total_mov = 0
            for actionstr, k in c.keyBinds.items():
                if keys[k]:
                    ares = self.actionMap[actionstr](c)
                    if ares == 'mov': total_mov += 1
            if total_mov == 0: self.reset(c)

        # global keybinds
        for k, action in self.keyMap.items():
            if keys[k]:
                starttime = time.clock()
                res = action()
                self.keyProfilerNum[k] += 1
                if self.speed_profiler:
                    self.keyProfilerSpeed[k].append(time.clock() - starttime)
                    # print(f"ran {k} handler {self.keyProfilerNum[k]} times with res: {res}; it took total {sum(self.keyProfilerSpeed[k])}s")

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
        self.screen.fill(BLACK)

        for _, comp_list in cmp_dict.items():
            for obj in comp_list:
                pos = obj.e.cmp_dict[self.cmps.Position]
                obj.render_shape(self.screen, pos.x, pos.y)

        self.pg.display.flip()
        return 1