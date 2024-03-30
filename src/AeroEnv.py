from Simulated import Simulated
from Vector import Vector

class AeroEnv(Simulated):
    def __init__(self, dispatcher, ID: int) -> None:
        super().__init__(dispatcher, ID, None)
        self.entities = []

    def getEntities(self) -> list:
        return self.entities

    def runSimulationStep(self, t: float = 1) -> None:
        for entity in self.getEntities():
            entity.runSimulationStep(t)

    def addEntity(self, entity):
        print("ent", entity)
        self.entities.append(entity)


class Airplane(Simulated):
    def __init__(self, dispatcher, ID: int, pos: Vector, vel: Vector) -> None:
        super().__init__(dispatcher, ID, pos)
        self.x, self.y, self.z = pos[0], pos[1], pos[2]
        # self.pos = pos
        self.vel = vel
        self.type_id = 1

    def runSimulationStep(self, t: int = 1) -> None:
        # print(self.pos, self.vel)

        self.pos = self.pos + self.vel


class Helicopter(Airplane):
    def __init__(self, dispatcher, ID: int, pos, vel) -> None:
        super().__init__(dispatcher, ID, pos, vel)
        self.type_id = 2


if __name__ == "__main__":
    import random
    n = random.randint(3, 10)
    targets = [Airplane(dispatcher=None, ID=i, pos=Vector(0, 0, 0), vel=Vector(1, 1, 1))
               if random.randint(1, 100) % 3 else Helicopter(dispatcher=None, ID=i, pos=Vector(0, 0, 0), vel=Vector(1, 1, 1))
               for i in range(n)]

    env = AeroEnv(None, len(targets))
    for el in targets:
        print(el.type_id)
        env.addEntity(el)

    print(env.getEntities())
