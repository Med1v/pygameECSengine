from mycolors import *
import math

# abstract system base class
class BasicSystem(object):
    def __init__(self, pg):
        self.pg = pg
        import components as cmps
        self.cmps = cmps


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

    def update(self, cmp_dict):
        pass


class PhysicsSystem(BasicSystem):
    def __init__(self, pg):
        super().__init__(pg)

    def playerMovement(self, pos, c):
        direction = c.e.cmp_dict[self.cmps.PlayerCtrl].direction
        if direction[0] == 1:
            pos.y -= c.speed
        if direction[1] == 1:
            pos.x += c.speed
        if direction[2] == 1:
            pos.y += c.speed
        if direction[3] == 1:
            pos.x -= c.speed

    def inertiaMovement(self, pos, c):
        direction = c.e.cmp_dict[self.cmps.PlayerCtrl].direction

        c.forces = [x * c.power for x in direction]

    def registerCollision(self, pos, c):
        pass

    def inertiaUpdate(self, pos, c):
        sign = lambda x: (1, -1)[x < 0]
        # friction absolute
        # fr_change = c.friction/c.weight

        # # if for making so friction applies only to net 0 axis
        # fr_speedx = sign(c.speedx)*fr_change if (c.forces[1] - c.forces[3]) == 0 else 0
        # fr_speedy = sign(c.speedy)*fr_change if (c.forces[2] - c.forces[0]) == 0 else 0

        # c.speedx -= fr_speedx if (abs(fr_speedx) < abs(c.speedx)) else c.speedx
        # c.speedy -= fr_speedy if (abs(fr_speedy) < abs(c.speedy)) else c.speedy

        # friction force
        direction = c.e.cmp_dict[self.cmps.PlayerCtrl].direction
        if c.speedy != 0:
            amount = c.friction if c.friction/c.weight < abs(c.speedy) else abs(c.speedy*c.weight)
            if c.speedy > 0:
                c.forces[0] += amount if not direction[2] else 0
            else:
                c.forces[2] += amount if not direction[0] else 0
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
                c.speedx = sign(c.speedx) * c.maxspeed if abs(c.speedx) > c.maxspeed else 0
                c.speedy = sign(c.speedy) * c.maxspeed if abs(c.speedy) > c.maxspeed else 0
            else:
                angle = math.atan(abs(c.speedy/c.speedx))
                c.speedx = sign(c.speedx) * math.cos(angle) * c.maxspeed
                c.speedy = sign(c.speedy) * math.sin(angle) * c.maxspeed

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
                if self.cmps.PlayerCtrl in c.e.cmp_dict:
                    self.playerMovement(pos, c)

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

        for _, comp_list in cmp_dict.items():
            for obj in comp_list:
                # no Transform - no render
                try: pos = obj.e.cmp_dict[self.cmps.Transform]
                except KeyError: continue
                # render here
                obj.render_shape(self.screen, pos.x, pos.y)

        self.pg.display.flip()
        return 1