import numpy as np

from src.constants import (GuidedMissile_SPEED, EPS,
                           GuidedMissile_LifeTime, GuidedMissile_ExplRadius,
                           GuidedMissile_MaxRotAngle, GuidedMissile_SIZE, GuidedMissile_ExplRadiusError,
                           MSG_RADAR2GM_type)
from src.messages_classes.Messages import GuidedMissileHit2RadarMsg
from src.modules_classes.ModelDispatcher import ModelDispatcher
from src.modules_classes.Movable import Movable, angle_between, dist
from logs.logger import logger


class GuidedMissile(Movable):
    def __init__(self, dispatcher: ModelDispatcher, ID: int,
                 pos: np.array, aero_env,
                 speed: int = GuidedMissile_SPEED,
                 life_time: int = GuidedMissile_LifeTime,
                 expl_radius: int = GuidedMissile_ExplRadius,
                 size: int = GuidedMissile_SIZE) -> None:
        """
        :param dispatcher: диспетчер, для синхронизации с другими модулями
        :param ID: ID этой ракеты
        :param pos: позиция цели в формате (x, y, z)
        :param speed: модуль скорости ракеты
        :param life_time: возможное время жизни ракеты
        :param expl_radius: радиус взрыва ракеты
        :param size: характерный рамзер ракеты
        """
        super(GuidedMissile, self).__init__(dispatcher, ID, pos, None, size, speed)
        self.radar_id = None
        self.aero_env = aero_env
        self.pos_target = None
        self.life_time = life_time
        self.expl_radius = expl_radius
        self.pos_target = None
        self.delay_time = 2  # задержка между ЗУР и ПБУ (в тактах)
        self.time2exploit = False
        self.status = 0
        self.launch_time = None
        self.target_vel = np.array([0., 0., 0.])

    def launch(self, pos_target: np.array([float, float, float]), radar_id: int, launch_time: float) -> None:

        """
        :param pos_target: np array of pos_objects (x, y, z)
        :param radar_id: ID радара, который будет общатсья с ЗУР, нужно чтобы отправлять сообщения,
         даже если их нет ос самого радара
        :param launch_time: время запуска
        :return:
        """
        self.pos_target = pos_target
        self.vel = (self.pos_target - self.pos + EPS) / (np.linalg.norm(self.pos_target - self.pos) + EPS) * self.speed
        self.launch_time = launch_time
        self.status = 1
        logger.guided_missile(
            f"Запуск. ЗУР ID: {self._ID}, начальная позиция: {self.pos}, начальная позиция цели: {self.pos_target}, общается с Радаром ID: {self.radar_id}")

    def updateTarget(self, pos_target: np.array([float, float, float]),
                     target_vel: np.array([float, float, float])) -> None:
        """
        Обновление координат цели
        :param target_vel: вектор скорости цели
        :param pos_target: положение цели
        :return:
        """
        self.target_vel = target_vel
        self.pos_target = pos_target + self.target_vel * self._simulating_tick

    def updateCoordinate(self) -> None:
        """
        Обновление координат ракеты
        :return:
        """
        vel_old = self.vel.copy()
        self.vel = ((self.pos_target - self.pos)
                    / np.linalg.norm(self.pos_target - self.pos) * self.speed)

        if angle_between(self.vel, vel_old) > GuidedMissile_MaxRotAngle:
            logger.guided_missile(f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos},"
                                  f" корректировка большого угла поворота {round(np.rad2deg(angle_between(self.vel, vel_old)), 2)}°")
            self.vel = (self.vel + vel_old) / np.linalg.norm(self.vel + vel_old) * self.speed

        # добавить задержку от передачи смс от ПБУ к РАДАРУ к ЗУР, чтобы расстояние до цели считалось верно
        dist2target = dist(self.pos_target + self.target_vel * self._simulating_tick * self.delay_time, self.pos)
        if dist2target < np.linalg.norm(self.vel * self._simulating_tick):
            self.pos = self.pos_target + self.target_vel * self._simulating_tick * self.delay_time
        else:
            self.pos = self.pos + self.vel * self._simulating_tick

    def checkIsHit(self):
        """
        Проверка поражена ли цель
        :return:
        """
        if dist(self.pos_target + self.target_vel * self._simulating_tick * self.delay_time,
                self.pos) < self.expl_radius - GuidedMissile_ExplRadiusError:
            self.status = 2
        logger.guided_missile(
            f"ЗУР ID: {self._ID}, pos_target {self.pos_target}, target_vel {self.target_vel},  pos {self.pos}")

        logger.guided_missile(
            f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, расстояние до цели: {(((self.pos - self.pos_target) ** 2).sum()) ** 0.5}, расстояние до цели интерполированное {(((self.pos_target + self.target_vel * self._simulating_tick * self.delay_time - self.pos) ** 2).sum()) ** 0.5}")

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
        :return:
        """
        messages = self._checkAvailableMessagesByType(msg_type=MSG_RADAR2GM_type)
        messages.sort(key=lambda x: x.priority, reverse=True)

        pos_target = self.pos_target
        target_vel = self.target_vel

        if len(messages) != 0:
            pos_target = messages[0].new_target_coord
            target_vel = messages[0].target_vel
            self.radar_id = messages[0].sender_ID
            logger.guided_missile(
                f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, получила сообщение от Радара ID: {self.radar_id}, новые координаты цели: {pos_target}, ее вектор скорости: {target_vel}")

        if self.status == 1:
            self.updateTarget(pos_target, target_vel)
            self.updateCoordinate()
            self.checkIsHit()
            if self.status == 2:
                logger.guided_missile(
                    f"ЗУР ID: {self._ID}, координаты ЗУР: {self.pos}, поразила цель с координатами: {self.pos_target}")

                # отправляет смс радару чтобы радар передал ПБУ и ПБУ забыла про это ЗУР и ее цель
                logger.guided_missile(
                    f"ЗУР ID: {self._ID}, отправила сообщение Радару {self.radar_id} о том, что она перестала существовать")

                msg2radar_hit = GuidedMissileHit2RadarMsg(time, self._ID, self.radar_id)
                self._sendMessage(msg2radar_hit)

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