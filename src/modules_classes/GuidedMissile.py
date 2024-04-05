import numpy as np

from src.modules_classes.ModelDispatcher import ModelDispatcher
from src.modules_classes.Movable import Movable
from src.messages_classes.BaseMessage import BaseMessage
from config.constants import (MSG_CCP2GM_type, GuidedMissile_SPEED,
                              GuidedMissile_LifeTime, GuidedMissile_ExplRadius, GuidedMissile_MaxRotAngle,
                              MSG_RADAR2GM_type)
from src.utils.logger import logger


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

        angle_between((1, 0, 0), (0, 1, 0))
        1.5707963267948966

        angle_between((1, 0, 0), (1, 0, 0))
        0.0

        angle_between((1, 0, 0), (-1, 0, 0))
        3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


class GuidedMissile(Movable):
    def __init__(self, dispatcher: ModelDispatcher, ID: int,
                 pos: np.array, aero_env,
                 speed=GuidedMissile_SPEED,
                 life_time=GuidedMissile_LifeTime,
                 expl_radius=GuidedMissile_ExplRadius,
                 size=2.0) -> None:
        """
        :param dispatcher: диспетчер, для синхронизации с другими модулями
        :param ID: ID этой ракеты
        :param pos: position of guide missile (x,y,z)
        :param speed:
        :param life_time: возможное время жизни ракеты
        :param expl_radius: радиус взрыва ракеты
        :param size: характерный рамзер ракеты
        """
        super(GuidedMissile, self).__init__(dispatcher, ID, pos, None, size)
        self.aero_env = aero_env
        self.speed = speed
        self.pos_target = None
        self.life_time = life_time
        self.expl_radius = expl_radius
        self.pos_target = None
        self.delay_time = 2
        self.time2exploit = False
        self.status = 0
        self.launch_time = None
        self.target_vel = np.array([0., 0., 0.])

    def launch(self, pos_target: np.array, launch_time: float) -> None:
        """
        :param pos_target: np array of pos_objects (x, y, z)
        :param launch_time: время запуска
        """
        self.pos_target = pos_target
        self.vel = (self.pos_target - self.pos) / (np.linalg.norm(self.pos_target - self.pos) + 0.0000001) * self.speed
        self.launch_time = launch_time
        self.status = 1
        logger.guided_missile(f"Запуск. ЗУР ID: {self._ID}, начальная позиция: {self.pos}, начальная позиция цели: {self.pos_target}")
        
    def updateTarget(self, pos_target: np.array([float, float, float]), target_vel: np.array([float, float, float])) -> None:
        """
        Обновление координат цели
        :param pos_target: np.array of [x,y,z]
        """

        self.target_vel = target_vel
        self.pos_target = pos_target + self.target_vel*self._simulating_tick

    def updateCoordinate(self) -> None:
        """
        Обновление координат ракеты
        :param time: сколько времени ракета летела с прошлого обновления координат
        """
        vel_old = self.vel.copy()
        self.vel = ((self.pos_target - self.pos)
                    / np.linalg.norm(self.pos_target - self.pos) * self.speed)

        if angle_between(self.vel, vel_old) > GuidedMissile_MaxRotAngle:
            logger.guided_missile(f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos},"
                                  f" корректировка большого угла поворота {round(np.rad2deg(angle_between(self.vel, vel_old)),2)}°")
            self.vel = (self.vel + vel_old) / np.linalg.norm(self.vel + vel_old) * self.speed


        # добавить задержку от передачи смс от ПБУ к РАДАРУ к ЗУР, чтобы расстояние до цели считалось верно
        dist2target = np.linalg.norm(self.pos_target+self.target_vel*self._simulating_tick*self.delay_time - self.pos)
        if dist2target < np.linalg.norm(self.vel*self._simulating_tick):
            self.pos = self.pos_target+self.target_vel*self._simulating_tick*self.delay_time

        else:
            self.pos = self.pos + self.vel*self._simulating_tick

    def checkIsHit(self):
        """
        Проверка поражена ли цель
        """
        if (((self.pos_target+self.target_vel*self._simulating_tick*self.delay_time - self.pos ) ** 2).sum())**0.5 < self.expl_radius:
            self.status = 2
        logger.guided_missile(
                f"ЗУР ID: {self._ID}, pos_target {self.pos_target}, target_vel {self.target_vel},  pos {self.pos}")

        logger.guided_missile(f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, расстояние до цели: {(((self.pos - self.pos_target) ** 2).sum()) ** 0.5}, расстояние до цели и нтерполированное {(((self.pos_target+self.target_vel*self._simulating_tick*self.delay_time - self.pos) ** 2).sum())**0.5}")

    def getStatus(self):
        """
        Узнать статус ракеты
        0 - не активна
        1 - летит
        2 - поразила цель
        3 - пропустила цель, закончилось топливо
        :return:
        """
        return self.status

    def runSimulationStep(self, time):
        """
        Шаг симуляции ракеты
        MSG_CCP2GM_type, сообщения корректирующие положение цели
        :param time: текущее время в симуляции
        """
        #logger.guided_missile(f"жду сообщения типа {MSG_CCP2GM_type}")
        messages = self._checkAvailableMessagesByType(msg_type=MSG_RADAR2GM_type)
        messages.sort(key=lambda x: x.priority, reverse=True)

        pos_target = self.pos_target
        target_vel = self.target_vel

        #logger.guided_missile(f"ЗУР ID: {self._ID}, получила сообщение от ПБУ, столько сообщение: {len(messages_classes)}")

        if len(messages) != 0:
            pos_target = messages[0].new_target_coord
            target_vel = messages[0].target_vel
            logger.guided_missile(f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, получила сообщение от Радара, новые координаты цели: {pos_target}, ее вектор скорости: {target_vel}")

        if self.status == 1:
            self.updateTarget(pos_target, target_vel)
            self.updateCoordinate()
            self.checkIsHit()
            if self.status == 2:
                logger.guided_missile(
                    f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, поразила цель с координатами: {self.pos_target}")
                self.aero_env.explosion(self.pos, self.expl_radius)
            elif time - self.launch_time > self.life_time:
                self.status = 3
                self.aero_env.explosion(self.pos, self.expl_radius)
                logger.guided_missile(
                    f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, пропустила цель с координатами: {self.pos_target}"
                    f"Кончилось топливо")

        if self.status > 1:
            logger.guided_missile(
                f"ЗУР ID: {self._ID} прекратила существоавние из-за {'поражения цели' if self.status == 2 else 'нехватки топлива'}")

        self.previous_time = time
