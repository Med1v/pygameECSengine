from mycolors import *
import math

# abstract system base class
class BasicSystem(object):
    def __init__(self, pg):
        self.pg = pg
        import components as cmps
        self.cmps = cmps
        self.ctrl_list = [cmps.PlayerCtrl, cmps.ChaseBotCtrl]

        self.sign = lambda x: (1, -1)[x < 0]


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

        # less precise, more human and yet awkward behaviour
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


class PhysicsSystem(BasicSystem):
    def __init__(self, pg):
        super().__init__(pg)

    def playerMovement(self, ctrl, pos, c):
        direction = c.e.cmp_dict[ctrl].direction
        if direction[0] == 1:
            pos.y -= c.speed
        if direction[1] == 1:
            pos.x += c.speed
        if direction[2] == 1:
            pos.y += c.speed
        if direction[3] == 1:
            pos.x -= c.speed

    def inertiaMovement(self, pos, c):
        for cp in self.ctrl_list:
            try: ctrl = c.e.cmp_dict[cp]
            except KeyError: continue

            direction = ctrl.direction
            c.forces = [x * c.power for x in direction]

    def registerCollision(self, pos, c):
        pass

    def inertiaUpdate(self, pos, c):
        # friction force
        for cp in self.ctrl_list:
            try: ctrl = c.e.cmp_dict[cp]
            except KeyError: continue
        direction = ctrl.direction
        # if not standing still
        if c.speedy != 0:
            # friction must be reduced if friction force is bigger than momentum
            amount = c.friction if c.friction < abs(c.speedy*c.weight) else abs(c.speedy*c.weight)
            # apply force depending on player's movement direction and input
            if c.speedy > 0:
                c.forces[0] += amount if not direction[2] else 0
            else:
                c.forces[2] += amount if not direction[0] else 0
        # same for other axis
        if c.speedx != 0:
            amount = c.friction if c.friction/c.weight < abs(c.speedx) else abs(c.speedx*c.weight)
            if c.speedx > 0:
                c.forces[3] += amount if not direction[1] else 0
            else:
                c.forces[1] += amount if not direction[3] else 0

        # force
        c.speedx += (c.forces[1] - c.forces[3])/c.weight
        c.speedy += (c.forces[2] - c.forces[0])/c.weight
        c.forces = [0, 0, 0, 0]

        # max speed
        curr_speed = math.sqrt(c.speedx**2 + c.speedy**2)
        if curr_speed > c.maxspeed:
            if c.speedy == 0 or c.speedx == 0:
                c.speedx = self.sign(c.speedx) * c.maxspeed if abs(c.speedx) > c.maxspeed else 0
                c.speedy = self.sign(c.speedy) * c.maxspeed if abs(c.speedy) > c.maxspeed else 0
            else:
                angle = math.atan(abs(c.speedy/c.speedx))
                c.speedx = self.sign(c.speedx) * math.cos(angle) * c.maxspeed
                c.speedy = self.sign(c.speedy) * math.sin(angle) * c.maxspeed

        # position
        pos.x += c.speedx
        pos.y += c.speedy

    def getPos(self, c):
        # if component's entity doesn't have transform it is irrelevant to physicsSystem
        try: return c.e.cmp_dict[self.cmps.Transform]
        except KeyError: None

    def update(self, cmp_dict):
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

        if self.cmps.CollisionBox in cmp_dict:
            for c in cmp_dict[self.cmps.CollisionBox]:
                pos = self.getPos(c)
                if pos is None: continue
                self.registerCollision(pos, c)

        if self.cmps.InertiaMovement in cmp_dict:
            for c in cmp_dict[self.cmps.InertiaMovement]:
                pos = self.getPos(c)
                if pos is None: continue
                self.inertiaUpdate(pos, c)

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