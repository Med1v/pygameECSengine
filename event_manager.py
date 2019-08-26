import time

class EventManager(object):
    """Registers event to eventually be handled in the main loop"""

    def __init__(self):
        super(EventManager, self).__init__()
        self.keyMap = {}
        self.keyProfilerNum = {}
        self.keyProfilerSpeed = {}
        self.speed_profiler = False

    def register_handler(self, key, handler):
        self.keyMap[key] = handler
        self.keyProfilerNum[key] = 0
        self.keyProfilerSpeed[key] = []
        print(self.keyMap)

    def handle(self, keys):
        res = 1

        for k, v in self.keyMap.items():
            if keys[k]:
                starttime = time.clock()
                res = v()
                self.keyProfilerNum[k] += 1
                if self.speed_profiler:
                    self.keyProfilerSpeed[k].append(time.clock() - starttime)
                    # print(f"ran {k} handler {self.keyProfilerNum[k]} times with res: {res}; it took total {sum(self.keyProfilerSpeed[k])}s")

        return res
