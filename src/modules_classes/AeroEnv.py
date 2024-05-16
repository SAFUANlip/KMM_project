from src.modules_classes.Simulated import Simulated, ModelDispatcher
from src.modules_classes.Movable import Movable, angle_between, dist
from src.modules_classes.GuidedMissile import GuidedMissile
from logs.logger import logger
from src.constants import (Airplane_MaxRotAngle, Airplane_SPEED, Airplane_SIZE, Airplane_DistUpdate, EPS, DISPATCHER_ID)
from src.messages_classes.Messages import AeroEnv_InitMessage, AeroEnv_ViewMessage

import numpy as np


class AeroEnv(Simulated):
    def __init__(self, dispatcher: ModelDispatcher, ID: int, targets: list[Movable]) -> None:
        """
        :param dispatcher: диспетчер, для синхронизации с другими модулями
        :param ID: ID воздушной обстановки
        :param targets: список целей класса Movable
        """
        super().__init__(dispatcher, ID, None)
        self.entities = []
        self.cur_time = 0  # ( ? )
        self.targets = targets
        self.start = True
    
    def getEntities(self) -> list:
        """
        :return: список существующих целей
        """
        return self.entities

    def runSimulationStep(self, time: float = 1) -> None:
        """
        Шаг симуляции для ВО
        :param time: текущее время
        :return:
        """
        if self.start:
            init_msg = AeroEnv_InitMessage(
                time=time,
                sender_ID=self._ID,
                receiver_ID=DISPATCHER_ID
            )
            self._sendMessage(init_msg)
            self.start = False

        not_launched_targets = []
        for target in self.targets:
            if target.start_time <= time:
                self.addEntity(target)
            else:
                not_launched_targets.append(target)
        self.targets = not_launched_targets

        to_del = []
        for entity in self.entities:
            if isinstance(entity, Airplane):
                if entity.start_time <= time < entity.end_time:
                    entity.runSimulationStep(time)
                else:
                    to_del.append(entity)
            else:
                entity.runSimulationStep(time)

        for el in to_del:
            self.entities.remove(el)
        logger.aero_env(f"AeroEnv имеет {len(self.entities)}")
        self.send_vis_objects2gui(time)

    def send_vis_objects2gui(self, time: float):
        """
        Отправка сообщений визуализатору с тем что видит ВО (цели и ракеты)
        :param time: текущее время
        :return:
        """
        missile_list = []
        target_list = []
        view_dict = {}

        for entity in self.entities:
            if isinstance(entity, Airplane):
                target_list.append((entity._ID, entity.pos))
            else:
                missile_list.append((entity._ID, entity.pos))

        view_dict["missiles"] = missile_list
        view_dict["targets"] = target_list

        msg2drawer = AeroEnv_ViewMessage(
            time=time,
            sender_ID=self._ID,
            receiver_ID=DISPATCHER_ID,
            view_dict=view_dict,
        )
        self._sendMessage(msg2drawer)
        logger.aero_env(f"ВО отправил GUI: {len(missile_list)} ЗУР и {len(target_list)} ЦЕЛЕЙ")

    def addEntity(self, entity: Movable) -> None:
        """
        Добавление цели в список существующих целей
        :param entity: Movable объект
        :return:
        """
        self.entities.append(entity)

    def explosion(self, pos: np.array([float, float, float]), expl_rad: float) -> None:
        """
        Взрыв ракеты, уничтожает все то попало в радиус взрыва
         + рекурсивно взрывает другие ракеты, если они попали в область
        :param pos: текущая позиция ракеты, где она взрывается
        :param expl_rad: радиус взрыва ракеты
        :return:
        """
        chain_explosion = []
        to_del = []
        logger.aero_env(
            f"AeroEnv количество объектов {len(self.entities)}")

        for el in self.entities:
            logger.aero_env(
                f"AeroEnv расстояние между ЗУР: {pos}, и объектом: {el.pos}, {dist(pos, el.pos)}, размер объекта {el.size}, радиус взрыва {expl_rad}")
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


class Airplane(Movable):
    def __init__(self, dispatcher: ModelDispatcher, ID: int, vel: np.array([float, float, float]),
                 size: float = Airplane_SIZE, speed: int = Airplane_SPEED,
                 trajectory_planned=[np.array([float, float, float])],
                 start_time: float = 0.0, end_time: float = np.inf) -> None:
        """
        Класс самолета
        :param dispatcher: диспетчер, для синхронизации с другими модулями
        :param ID: ID самолета
        :param vel: вектор скорости самолета
        :param size: характерный размер самолета
        :param speed: скорость самолета (модуль)
        :param trajectory_planned: траектория полета самолета, [0] элемент - это начальное положение,
         остальные - контрольные точки
        :param start_time: когда самолет начинает свое существование и появится в ВО
        :param end_time: когда самолет закончит свое существование и исчезнит из ВО
        """
        super().__init__(dispatcher, ID, pos=trajectory_planned[0],
                         vel=vel if vel is not None else np.array([Airplane_SPEED, 0, 0]), size=size, speed=speed)
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
        """
        Шаг симуляции для самолета
        :param time: текущее время
        :return:
        """
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
        self.trajectory.append(self.pos)
