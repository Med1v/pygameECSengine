import time


class BasicSystem(object):
    def __init__(self, pg):
        self.pg = pg
        self.cemap = {}

    def addComponent(self, cmp, ent):
        self.cemap[cmp] = ent


class RenderSystem(BasicSystem):
    def __init__(self, pg):
        super(RenderSystem, self).__init__(pg)

    def update(self):
        return 1


class HandlerSystem(BasicSystem):
    def __init__(self, pg):
        super(HandlerSystem, self).__init__(pg)
        self.keyMap = {}
        self.keyProfilerNum = {}
        self.keyProfilerSpeed = {}
        self.speed_profiler = False

        def onEscape():
            return 0
        self.addKey(pg.K_ESCAPE, onEscape)

        def onEnter():
            print("Enter pressed")
            return 1
        self.addKey(pg.K_RETURN, onEnter)

    def addKey(self, k, f):
        self.keyMap[k] = f
        self.keyProfilerNum[k] = 0
        self.keyProfilerSpeed[k] = []

    def update(self):
        res = 1

        keys = self.pg.key.get_pressed()
        for k, v in self.keyMap.items():
            if keys[k]:
                starttime = time.clock()
                res = v()
                self.keyProfilerNum[k] += 1
                if self.speed_profiler:
                    self.keyProfilerSpeed[k].append(time.clock() - starttime)
                    # print(f"ran {k} handler {self.keyProfilerNum[k]} times with res: {res}; it took total {sum(self.keyProfilerSpeed[k])}s")

        return res