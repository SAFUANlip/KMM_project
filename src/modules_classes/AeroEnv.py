from src.modules_classes.Simulated import Simulated
from src.modules_classes.Movable import Movable, angle_between, dist
from src.modules_classes.GuidedMissile import GuidedMissile
from src.utils.logger import logger
from config.constants import Airplane_MaxRotAngle, Airplane_SPEED, Airplane_SIZE, Airplane_DistUpdate, EPS

import numpy as np
import random
import copy


class AeroEnv(Simulated):
    def __init__(self, dispatcher, ID: int, targets: list) -> None:
        super().__init__(dispatcher, ID, None)
        # self.unpacked_entities = []
        self.entities = []
        self.cur_time = 0  # ( ? )
        self.targets = targets
    
    def getEntities(self) -> list:
        return self.entities

    def runSimulationStep(self, time: float = 1) -> None:
        not_launched_targets = []
        for target in self.targets:
            if target.start_time <= time:
                self.addEntity(target)
            else:
                not_launched_targets.append(target)
        self.targets = not_launched_targets

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
        to_del = []
        logger.aero_env(
            f"AeroEnv количество объектов {len(self.entities)}")

        for el in self.entities:
            logger.aero_env(
                f"AeroEnv расстояние между ЗУР и объектом {dist(pos, el.pos)}, размер объекта {el.size}, радиус взрыва {expl_rad}")
            if dist(pos, el.pos) - el.size < expl_rad:
                if isinstance(el, GuidedMissile) and (el.pos != pos).all():
                    chain_explosion.append((el.pos, el.expl_radius))
                to_del.append(el)

        for el in to_del:
            self.entities.remove(el)
            logger.aero_env(
                f"AeroEnv взрыв ЗУР с координатами: {pos}, Уничтожила цель с ID: {el._ID} и координатами {el.pos}")

        # chain reaction
        for pos, expl_rad in chain_explosion:
            self.explosion(pos, expl_rad)

    def allTrajectories(self):
        trajectories = []
        for el in self.entities:
            if isinstance(el, Airplane) or isinstance(el, Helicopter):
                trajectories.append(el)
        return trajectories


class Airplane(Movable):
    def __init__(self, dispatcher, ID: int, size=Airplane_SIZE, speed=Airplane_SPEED,
                 trajectory_planned=[], start_time: float = 0.0, end_time: float = np.inf) -> None:
        super().__init__(dispatcher, ID, pos=trajectory_planned[0], vel=np.array([speed, 0, 0]), size=size, speed=speed)
        self.type_id = 1
        self.trajectory = [trajectory_planned[0]]
        self.trajectory_planned = trajectory_planned
        self.start_time = start_time
        self.end_time = end_time
        self.cur_time = start_time
        self.target_point = self.trajectory_planned[1] if len(self.trajectory_planned) > 1 else None

        self.trajectory_planned.pop(0)
        if self.target_point is not None:
            self.vel = (self.target_point - self.pos + EPS) / (
                        np.linalg.norm(self.target_point - self.pos) + EPS) * self.speed

    def runSimulationStep(self, time: float = 1.0) -> None:
        if self.target_point is not None:
            if dist(self.target_point, self.pos) <= Airplane_DistUpdate:
                if len(self.trajectory_planned) > 0:
                    self.target_point = self.trajectory_planned.pop(0)
                    logger.airplane(
                        f"Самолет ID: {self._ID}, Новая контрольная точка: {self.target_point}")
                else:
                    self.target_point = None
                    logger.airplane(f"Самолет ID: {self._ID},"
                                    f" прошел все контрольные точки, летит по вектору: {self.vel}")
            else:
                vel_old = self.vel.copy()
                self.vel = (self.target_point - self.pos + EPS) / (
                        np.linalg.norm(self.target_point - self.pos) + EPS) * self.speed

                if angle_between(self.vel, vel_old) > Airplane_MaxRotAngle:
                    logger.airplane(f"Самолет ID: {self._ID}, координаты Самолета: {self.pos},"
                                          f" корректировка большого угла поворота {round(np.rad2deg(angle_between(self.vel, vel_old)), 2)}°")
                    self.vel = (self.vel + vel_old + EPS) / np.linalg.norm(self.vel + vel_old + EPS) * self.speed

        if self.target_point is not None:
            dist2target_point = dist(self.target_point, self.pos + self.vel * self._simulating_tick)
            if dist2target_point < np.linalg.norm(self.vel * self._simulating_tick):
                if len(self.trajectory_planned) > 0:
                    self.target_point = self.trajectory_planned.pop(0)
                    logger.airplane(
                        f"Самолет ID: {self._ID}, Новая контрольная точка: {self.target_point}")
                else:
                    self.target_point = None
                    self.target_point = None
                    logger.airplane(f"Самолет ID: {self._ID},"
                                    f" прошел все контрольные точки, летит по вектору: {self.vel}")

        self.pos = self.pos + self.vel * self._simulating_tick
        self.cur_time += self._simulating_tick
        self.trajectory.append((self.pos, self.cur_time))



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