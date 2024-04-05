from src.modules_classes.Simulated import Simulated
from src.modules_classes.Movable import Movable
from src.modules_classes.GuidedMissile import GuidedMissile
from src.utils.logger import logger

import numpy as np
import random
import copy


class AeroEnv(Simulated):
    def __init__(self, dispatcher, ID: int) -> None:
        super().__init__(dispatcher, ID, None)
        # self.unpacked_entities = []
        self.entities = []
        self.cur_time = 0  # ( ? )
    
    def getEntities(self) -> list:
        return self.entities

    def runSimulationStep(self, time: float = 1) -> None:
        for entity in self.entities:
            if isinstance(entity, Airplane) or isinstance(entity, Helicopter):
                if entity.start_time <= time < entity.end_time:
                    entity.runSimulationStep(time)
            else:
                entity.runSimulationStep(time)
        logger.aero_env(f"AeroEnv имеет {len(self.entities)}")

    def addEntity(self, entity) -> None:
        self.entities.append(entity)

    def explosion(self, pos: np.array, expl_rad: float) -> None:
        chain_explosion = []
        for el in self.entities:
            logger.aero_env(
                f"AeroEnv расстояние между ЗУР и объектом {self.dist(pos, el.pos)}, размер объекта {el.size}, радиус взрыва {expl_rad}")
            if self.dist(pos, el.pos) - el.size < expl_rad:
                if isinstance(el, GuidedMissile) and (el.pos != pos).all():
                    chain_explosion.append((el.pos, el.expl_radius))
                self.entities.remove(el)
                logger.aero_env(f"AeroEnv взрыв ЗУР с координатами: {pos}, Уничтожила цель с ID: {el._ID} и координатами {el.pos}")

        # chain reaction
        for pos, expl_rad in chain_explosion:
            self.explosion(pos, expl_rad)

    def dist(self, pos1: np.array, pos2: np.array) -> float:
        return np.linalg.norm(pos1 - pos2)

    def allTrajectories(self):
        trajectories = []
        for el in self.entities:
            if isinstance(el, Airplane) or isinstance(el, Helicopter):
                trajectories.append(el)
        return trajectories


class Airplane(Movable):
    def __init__(self, dispatcher, ID: int, pos: np.array, size: float, vel: np.array,
                 start_time: float = 0.0, end_time: float = np.inf) -> None:
        super().__init__(dispatcher, ID, pos, vel, size)
        self.vel = vel
        self.type_id = 1
        self.trajectory = [pos]
        self.start_time = start_time
        self.end_time = end_time
        self.cur_time = start_time

    def runSimulationStep(self, time: float = 1.0) -> None:
        # print(self.pos, self.vel)
        self.pos = self.pos + self.vel * self._simulating_tick  # cur_time:TODO: Было неправильное время (ты умножал на cur_time)
        self.cur_time += self._simulating_tick
        self.trajectory.append((self.pos, self.cur_time))

    # def pos_copy(self) -> np.array:
    #     return copy.deepcopy(self.pos)


class Helicopter(Airplane):
    def __init__(self, dispatcher, ID: int, pos, size, vel, start_time, end_time) -> None:
        super().__init__(dispatcher, ID, pos, size, vel, start_time, end_time)
        self.type_id = 2


if __name__ == "__main__":
    n = random.randint(3, 10)
    targets = [
                Airplane(dispatcher=None, ID=i, pos=np.array([0, 0, 0]), size=5, vel=np.array([1, 1, 1]),
                         start_time=0, end_time=10)

                if random.randint(1, 100) % 3 else

                Helicopter(dispatcher=None, ID=i, pos=np.array([0, 0, 0]), size=5,
                           vel=np.array([1, 1, 1]), start_time=0, end_time=10)

                for i in range(n)
    ]

    env = AeroEnv(None, len(targets))
    for el in targets:
        env.addEntity(el)