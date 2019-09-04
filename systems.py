from mycolors import *
import math
import time

# abstract system base class
class BasicSystem(object):
    def __init__(self, pg):
        self.pg = pg
        import components as cmps
        self.cmps = cmps

        self.ctrl_list = [cmps.PlayerCtrl, cmps.ChaseBotCtrl]
        self.sign = lambda x: (1, -1)[x < 0]
        self.get_time = lambda: time.time() * 10  # time scale
        self.last_time = -1
        self.dt = 0

    def updatedt(self):
        if self.last_time == -1:
            self.last_time = self.get_time()
            self.dt = 0
            return
        curr_time = self.get_time()
        self.dt = curr_time - self.last_time
        self.last_time = curr_time

    def getPos(self, c):
        # if component's entity doesn't have transform it is irrelevant to physicsSystem
        try: return c.e.cmp_dict[self.cmps.Transform]
        except KeyError: None

# Basically a key event listener
class HandlerSystem(BasicSystem):
    def __init__(self, pg):
        super().__init__(pg)
        # dict of key:f(): if 'key' ressed then run function f() on the player
        self.keyMap = {}

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
            pl.direction = [0, 0, 0, 0]
            return 'stp'

        def plaUp(pl):
            pl.direction[0] = 1
            return 'mov'

        def plaRight(pl):
            pl.direction[1] = 1
            return 'mov'

        def plaDown(pl):
            pl.direction[2] = 1
            return 'mov'

        def plaLeft(pl):
            pl.direction[3] = 1
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

    # if movement key wasn't pressed then stop player
    def reset(self, pl):
        pl.direction = [0, 0, 0, 0]

    # called in main loop
    def update(self, cmp_dict):
        res = 1

        keys = self.pg.key.get_pressed()

        # player keybinds
        for c in cmp_dict[self.cmps.PlayerCtrl]:
            total_mov = 0
            # go through custom player keybinds
            self.reset(c)
            for actionstr, k in c.keyBinds.items():
                if keys[k]:
                    ares = self.actionMap[actionstr](c)
                    if ares == 'mov': total_mov += 1

        # global keybinds
        for k, action in self.keyMap.items():
            if keys[k]:
                # global keybinds define state of the app (like exit/pause)
                res = action()

        return res


class BotSystem(BasicSystem):
    def __init__(self, pg):
        super().__init__(pg)

    def chaseBotUpdate(self, pl_list, c):
        # find closest player
        try: bot_pos = c.e.cmp_dict[self.cmps.Transform]
        except KeyError: return
        pl_pos = None
        curr_d = 999999
        for p in pl_list:
            try: pos = p.e.cmp_dict[self.cmps.Transform]
            except KeyError: continue

            d = math.sqrt((bot_pos.x - pos.x)**2 + (bot_pos.y - pos.y)**2)
            if d < curr_d:
                pl_pos = pos
                curr_d = d
        if pl_pos is None: return

        # calculate movement
        xdif = bot_pos.x - pl_pos.x
        ydif = bot_pos.y - pl_pos.y

        # less precise, more awkward and yet realistic behaviour
        # getabs = lambda n, m: abs(n) if m == 0 else abs(n/m) # division by 0 handling
        # c.direction = [
        #     1 if self.sign(ydif) > 0 and getabs(ydif, xdif) > 0.5 else 0,  # up
        #     1 if self.sign(xdif) < 0 and getabs(xdif, ydif) > 0.5 else 0,  # right
        #     1 if self.sign(ydif) < 0 and getabs(ydif, xdif) > 0.5 else 0,  # down
        #     1 if self.sign(xdif) > 0 and getabs(xdif, ydif) > 0.5 else 0  # left
        # ]

        # precise bot-like behaviour
        c.direction = [
            1 if self.sign(ydif) > 0 else 0,  # up
            1 if self.sign(xdif) < 0 else 0,  # right
            1 if self.sign(ydif) < 0 else 0,  # down
            1 if self.sign(xdif) > 0 else 0  # left
        ]

    def update(self, cmp_dict):
        if self.cmps.ChaseBotCtrl in cmp_dict:
            for c in cmp_dict[self.cmps.ChaseBotCtrl]:
                self.chaseBotUpdate(cmp_dict[self.cmps.PlayerCtrl], c)


class CollisionSystem(BasicSystem):
    def __init__(self, pg, dimensions):
        super().__init__(pg)
        self.CELL_SIZE = 50
        # self.grid = [[None for _ in range(dimensions[1] / CELL_SIZE)] for _ in range(dimensions[0] / CELL_SIZE)]
        self.grid = {}
        self.cmp_occ = {}  # component occupancy

    def collide(self, c, el, d):
        # print(f"{c.e.id} collided with {el.e.id}")
        # el.e.cmp_dict[self.cmps.Square].color = (0, 255, 0)
        if self.cmps.InertiaMovement not in c.e.cmp_dict: return
        cinertia = c.e.cmp_dict[self.cmps.InertiaMovement]
        # xforce = cinertia.mass * ()
        # el.forces = []

    def doCollision(self, c, pos):
        # BUG: applies 2 times for both components
        res = []

        for p in self.cmp_occ[c]:
            for el in self.grid[p]:
                # don't collide with yourself
                if c == el: continue
                # get element position
                elpos = self.getPos(el)
                if elpos is None: continue

                # calculate collisions
                cleft = pos.x - c.w/2
                cright = pos.x + c.w/2
                ctop = pos.y - c.h/2
                cbottom = pos.y + c.h/2

                elleft = elpos.x - el.w/2
                elright = elpos.x + el.w/2
                eltop = elpos.y - el.h/2
                elbottom = elpos.y + el.h/2

                left_col = 1 if elleft < cleft < elright else 0
                right_col = 1 if elleft < cright < elright else 0
                top_col = 1 if eltop < ctop < elbottom else 0
                bottom_col = 1 if eltop < cbottom < elbottom else 0

                # if collision occures collide (TODO: respectively to direction)
                if left_col or right_col or top_col or bottom_col:
                    self.collide(c, el, [top_col, right_col, bottom_col, left_col])

        return res

    def updateGrid(self, cmp_list):
        # TODO: refresh previous grid instead of creating new
        # TODO: temporal coherence
        self.grid = {}
        for c in cmp_list:
            pos = self.getPos(c)
            if pos is None: continue

            # calculate collision box corners
            dw = c.w/2; dh = c.h/2
            tl = (int((pos.x - dw)/self.CELL_SIZE), int((pos.y - dh)/self.CELL_SIZE))
            tr = (int((pos.x + dw)/self.CELL_SIZE), int((pos.y - dh)/self.CELL_SIZE))
            bl = (int((pos.x - dw)/self.CELL_SIZE), int((pos.y + dh)/self.CELL_SIZE))
            br = (int((pos.x + dw)/self.CELL_SIZE), int((pos.y + dh)/self.CELL_SIZE))
            occupy_points = set([tl, tr, bl, br])

            # add component to collision grid and component occupancy dict
            for op in occupy_points:
                try: self.grid[op].append(c)
                except KeyError: self.grid[op] = [c]
                self.cmp_occ[c] = occupy_points

    def update(self, cmp_dict):
        # extend CollisionBox from general Collision class? or updateGrid([[cmp, cmp], [cmp, cmp]])
        if self.cmps.CollisionBox in cmp_dict:
            self.updateGrid(cmp_dict[self.cmps.CollisionBox])
            for c in cmp_dict[self.cmps.CollisionBox]:
                pos = self.getPos(c)
                if pos is None: continue
                self.doCollision(c, pos)


class PhysicsSystem(BasicSystem):
    def __init__(self, pg):
        super().__init__(pg)

    def playerMovement(self, ctrl, pos, c):
        direction = c.e.cmp_dict[ctrl].direction
        speed = c.speed * self.dt
        if direction[0] == 1:
            pos.y -= speed
        if direction[1] == 1:
            pos.x += speed
        if direction[2] == 1:
            pos.y += speed
        if direction[3] == 1:
            pos.x -= speed

    def inertiaMovement(self, pos, c):
        for cp in self.ctrl_list:
            try: ctrl = c.e.cmp_dict[cp]
            except KeyError: continue

            d = ctrl.direction
            # calculate new force depending on direction pressed and
            # divided by the ammount of directions that force gets applied to
            # so diagonal movement isn't 2 times stronger in total
            dsum = 1 if sum(d) == 0 else sum(d)
            forcex = d[1] * c.power - d[3] * c.power
            forcey = d[2] * c.power - d[0] * c.power
            c.forces = [c.forces[0] + forcex/dsum, c.forces[1] + forcey/dsum]

    def inertiaUpdate(self, pos, c):
        # friction force
        # for cp in self.ctrl_list:
        #     try: ctrl = c.e.cmp_dict[cp]
        #     except KeyError: continue

        #     direction = ctrl.direction
        #     # if not standing still
        #     if c.speed[1] != 0:
        #         # friction must be reduced if friction force is bigger than momentum
        #         amount = c.friction if c.friction < abs(c.speed[1]*c.mass) else abs(c.speed[1]*c.mass)
        #         # apply force depending on player's movement direction and input
        #         if c.speed[1] > 0:
        #             c.forces[0] += amount if not direction[2] else 0
        #         else:
        #             c.forces[0] += -amount if not direction[0] else 0
        #     # same for other axis
        #     if c.speed[0] != 0:
        #         amount = c.friction if c.friction < abs(c.speed[0]*c.mass) else abs(c.speed[0]*c.mass)
        #         if c.speed[0] > 0:
        #             c.forces[1] += amount if not direction[1] else 0
        #         else:
        #             c.forces[1] += -amount if not direction[3] else 0

        # force
        c.speed[0] += c.forces[0]/c.mass
        c.speed[1] += c.forces[1]/c.mass
        c.forces = [0, 0, 0, 0]

        # max speed
        curr_speed = math.sqrt(c.speed[0]**2 + c.speed[1]**2)
        if curr_speed > c.maxspeed:
            if c.speed[1] == 0 or c.speed[0] == 0:
                c.speed[0] = self.sign(c.speed[0]) * c.maxspeed if abs(c.speed[0]) > c.maxspeed else 0
                c.speed[1] = self.sign(c.speed[1]) * c.maxspeed if abs(c.speed[1]) > c.maxspeed else 0
            else:
                angle = math.atan(abs(c.speed[1]/c.speed[0]))
                c.speed[0] = self.sign(c.speed[0]) * math.cos(angle) * c.maxspeed
                c.speed[1] = self.sign(c.speed[1]) * math.sin(angle) * c.maxspeed

        # position
        pos.x += c.speed[0] * self.dt
        pos.y += c.speed[1] * self.dt

    def update(self, cmp_dict):
        self.updatedt()
        # Iterate through each component type in desired order
        if self.cmps.BasicMovement in cmp_dict:
            for c in cmp_dict[self.cmps.BasicMovement]:
                pos = self.getPos(c)
                if pos is None: continue
                for ctrl in self.ctrl_list:
                    if ctrl in c.e.cmp_dict:
                        self.playerMovement(ctrl, pos, c)

        if self.cmps.InertiaMovement in cmp_dict:
            for c in cmp_dict[self.cmps.InertiaMovement]:
                pos = self.getPos(c)
                if pos is None: continue
                self.inertiaMovement(pos, c)

        if self.cmps.InertiaMovement in cmp_dict:
            for c in cmp_dict[self.cmps.InertiaMovement]:
                pos = self.getPos(c)
                if pos is None: continue
                self.inertiaUpdate(pos, c)

        self.last_time = self.get_time()
        return 1


class RenderSystem(BasicSystem):
    def __init__(self, pg, screen):
        super().__init__(pg)
        self.screen = screen

    def update(self, cmp_dict):
        # clear frame with background color
        self.screen.fill(BLACK)

        for c in cmp_dict[self.cmps.Square]:
            # no Transform - no render
            try: pos = c.e.cmp_dict[self.cmps.Transform]
            except KeyError: continue
            # render here
            c.render_shape(self.screen, pos.x - c.size/2, pos.y - c.size/2)

        self.pg.display.flip()
        return 1