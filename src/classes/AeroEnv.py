from src.classes.Simulated import Simulated
from src.classes.Movable import Movable

import numpy as np
import copy


class AeroEnv(Simulated):
    def __init__(self, dispatcher, ID: int) -> None:
        super().__init__(dispatcher, ID, None)
        self.unpacked_entities = []
        self.entities = []
        self.t = 0 # ( ? )
    
    def getEntities(self) -> list:
        return self.entities

    def runSimulationStep(self, t: float = 1) -> None:
        alive_entities = []
        for entity in self.unpacked_entities:
            if entity.t_start <= t < entity.t_end:
                entity.runSimulationStep(t)
                alive_entities.append(entity)
        self.entities = alive_entities

    def addEntity(self, entity) -> None:
        self.unpacked_entities.append(entity)

    def explosion(self, pos: np.array, expl_rad: float) -> None:
        updated_entities = []
        chain_explosion = []
        for el in self.entities:
            if not (self._dist(pos, el.pos()) - el.rad < expl_rad):
                updated_entities.append(el)
            else:
                # chain reaction
                # if el.type_id == missle_type_id:
                #     chain_explosion.append(el.pos())
                pass
        self.entities = updated_entities
        for pos in chain_explosion:
            self.explosion(pos, expl_rad)

    def _dist(self, pos1: np.array, pos2: np.array) -> float:
        return np.linalg.norm(pos1 - pos2)

    def all_trajectories(self):
        return [t.trajectory for t in self.unpacked_entities]



class Airplane(Movable):
    def __init__(self, dispatcher, ID: int, pos: np.array, rad: float, vel: np.array,t_start: float, t_end: float) -> None:
        super().__init__(dispatcher, ID, pos, vel)
        self.vel = vel
        self.type_id = 1
        self.trajectory = [pos]
        self.rad = rad
        self.t_start = t_start
        self.t_end = t_end
        self.t = t_start

    def runSimulationStep(self, t: float = 1.0) -> None:
        # print(self.pos, self.vel)
        self.pos = self.pos + self.vel * t
        self.t += self._simulating_tick
        self.trajectory.append((self.pos, self.t))

    # def pos_copy(self) -> np.array:
    #     return copy.deepcopy(self.pos)


class Helicopter(Airplane):
    def __init__(self, dispatcher, ID: int, pos, rad, vel, t_start, t_end) -> None:
        super().__init__(dispatcher, ID, pos, rad, vel, t_start, t_end)
        self.type_id = 2


if __name__ == "__main__":
    import random
    n = random.randint(3, 10)
    targets = [
                Airplane(dispatcher=None, ID=i, pos=np.array([0, 0, 0]), rad=5, vel=np.array([1, 1, 1]),
                          t_start=0, t_end=10)

                if random.randint(1, 100) % 3 else

                Helicopter(dispatcher=None, ID=i, pos=np.array([0, 0, 0]), rad=5,
                          vel=np.array([1, 1, 1]),  t_start=0, t_end=10)

                for i in range(n)
    ]

    env = AeroEnv(None, len(targets))
    for el in targets:
        env.addEntity(el)