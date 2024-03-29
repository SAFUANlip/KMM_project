from src.classes.Simulated import Simulated
from src.classes.Movable import Movable
from src.classes.GuidedMissile import GuidedMissile
from src.utils.logger import logger

import numpy as np
import copy


class AeroEnv(Simulated):
    def __init__(self, dispatcher, ID: int) -> None:
        super().__init__(dispatcher, ID, None)
        # self.unpacked_entities = []
        self.entities = []
        self.t = 0 # ( ? )
    
    def getEntities(self) -> list:
        return self.entities

    def runSimulationStep(self, t: float = 1) -> None:
        for entity in self.entities:
            if isinstance(entity, Airplane) or isinstance(entity, Helicopter):
                if entity.t_start <= t < entity.t_end:
                    entity.runSimulationStep(t)
            else:
                #logger.aero_env(f"AeroEnv добавила ЗУР ID {entity._ID}")
                entity.runSimulationStep(t) # TODO: тут не было запуска шага симуляции, почему?!(
        logger.aero_env(f"AeroEnv имеет {len(self.entities)}")

    def addEntity(self, entity) -> None:
        self.entities.append(entity)

    def explosion(self, pos: np.array, expl_rad: float) -> None:
        updated_entities = []
        chain_explosion = []
        for el in self.entities:
            if not (self._dist(pos, el.pos) - el.rad < expl_rad):
                updated_entities.append(el)
            else:
                # chain reaction
                if isinstance(el, GuidedMissile):
                    chain_explosion.append((el.pos, el.expl_radius))

        self.entities = updated_entities
        for pos, expl_rad in chain_explosion:
            self.explosion(pos, expl_rad)

    def _dist(self, pos1: np.array, pos2: np.array) -> float:
        return np.linalg.norm(pos1 - pos2)

    def all_trajectories(self):
        trajectories = []
        for el in self.entities:
            if isinstance(el, Airplane) or isinstance(el, Helicopter):
                trajectories.append(el)
        return trajectories


class Airplane(Movable):
    def __init__(self, dispatcher, ID: int, pos: np.array, rad: float, vel: np.array,
                 t_start: float = 0.0, t_end: float = np.inf) -> None:
        super().__init__(dispatcher, ID, pos, vel, rad)
        self.vel = vel
        self.type_id = 1
        self.trajectory = [pos]
        self.t_start = t_start
        self.t_end = t_end
        self.t = t_start

    def runSimulationStep(self, t: float = 1.0) -> None:
        # print(self.pos, self.vel)
        self.pos = self.pos + self.vel * self._simulating_tick  # t:TODO: Было неправильное время (ты умножал на t)
        self.t += self._simulating_tick
        self.trajectory.append((self.pos, self.t))

    # def pos_copy(self) -> np.array:
    #     return copy.deepcopy(self.pos)


class Helicopter(Airplane):
    def __init__(self, dispatcher, ID: int, pos, rad, vel, t_start, t_end) -> None:
        super().__init__(dispatcher, ID, pos, rad, vel, t_start, t_end)
        self.type_id = 2


if __name__ == "__main__":
    import random #TODO: импорты наверх
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