class Entity(object):
    def __init__(self, id, manager):
        self.id = id
        self.manager = manager
        self.cmp_list = []  # probably not needed

    def addComponent(self, c):
        self.cmp_list.append(c)
        self.manager.newEC(self, c)


def init(mng):
    elist = []

    player = Entity('player0', mng)
    elist.append(player)

    return elist