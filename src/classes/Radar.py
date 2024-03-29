import numpy as np
from src.messages.Messages import Radar2CombatControlMsg
from src.classes.Simulated import Simulated
from src.classes.AeroEnv import AeroEnv
from src.utils.logger import logger


class RadarRound(Simulated):
    def __init__(self, dispatcher, ID: int, cp_ID: int, aero_env: AeroEnv,
                 pos: np.array, pan_start, tilt_start, view_distance: int,
                 pan_per_sec: float, tilt_per_sec: float):
        """ Класс, описывающий работу РЛС кругового типа обзора, является родительским классом
         для РЛС секторного типа обзора:
         :param dispatcher: ссылка на объект диспетчера
         :param ID: собственный ID
         :param cp_ID: ID ПБУ
         :param pos: координаты положения РЛС, относительно глобальной СК (x, y, z)
         :param pan_start: начальное положение по углу поворота относительно глобальной СК в градусах
         :param tilt_start: начальное положение по углу наклона относительно глобальной СК в градусах
         :param view_distance: дальность обзора РЛС
         :param pan_per_sec: угол раскрыва по углу поворота за секунду обзора в градусах
         :param tilt_per_sec: угол раскрыва по углу наклона за секунду обзора в градусах"""
        super().__init__(dispatcher, ID, pos)
        self.cp_ID = cp_ID
        self.aero_env = aero_env
        self.pan_start = pan_start
        self.tilt_start = tilt_start  # на потом

        self.pan_cur = pan_start  # начало секундного сектора обзора в данный момент времени по углу поворота
        self.tilt_cur = tilt_start  # начало секундного сектора обзора в данный момент времени по углу наклона

        # параметры зависящие от типа рлс
        self.view_distance = view_distance
        self.pan_per_sec = pan_per_sec
        self.tilt_per_sec = tilt_per_sec

    def findObjects(self):
        all_objects = self.aero_env.getEntities()
        visible_objects = []
        for obj in all_objects:
            r = np.linalg.norm(obj.pos - self.pos)
            eps = 0.0001
            if r < self.view_distance:
                # FIXME: считать относительно себя
                x, y, z = obj.pos
                # FIXME: проверить обзор видимый по формулам геометрии, а не из интернета
                tilt = np.arcsin(z / (r + eps))
                pan = np.arcsin(y / ((r * np.cos(tilt)) + eps))
                logger.radar(f"Pan and tilt of aim: {pan, tilt}")
                if self.pan_cur < pan < self.pan_cur + self.pan_per_sec and self.tilt_cur < tilt < self.tilt_cur + self.tilt_per_sec:
                    pos = obj.pos + np.random.randint(-int(0.001 * r) - 1, int(0.001 * r) + 1, size=3)

                    speed = np.linalg.norm(obj.vel)

                    velocity_from_radar = obj.vel + np.random.randint(-int(0.001 * speed) - 1, int(0.001 * speed) + 1, size=3)
                    speed_from_radar = np.linalg.norm(velocity_from_radar)
                    visible_objects.append([pos, velocity_from_radar, speed_from_radar])

        logger.radar(f"Radar с id {self._ID} видит {len(visible_objects)} объектов, координата первого: {visible_objects[0][0]}")
        return visible_objects

    def moveToNextSector(self):
        # винтовой обзор
        # FIXME: писать текущие углы обзора от того то до того то
        logger.radar(f"Radar ID {self._ID} pan_cur = {self.pan_cur} pan_per_sec = {self.pan_per_sec}")
        logger.radar(f"Radar ID {self._ID} tilt_cur = {self.tilt_cur} tilt_per_sec = {self.tilt_per_sec}")
        self.pan_cur = (self.pan_cur + self.pan_per_sec) % 360
        if self.pan_cur == self.pan_start:
            self.tilt_cur = (self.tilt_cur + self.tilt_per_sec) % 180


    # def runSimulationStep(self, time: int):
    #     visible_objects = self.find_objects()
    #     msg = Radar2CombatControlMsg(time, self._ID, self.cp_ID, visible_objects)
    #     self._sendMessage(msg)
    #     self.move_to_next_sector()

    def runSimulationStep(self, time: float):
        visible_objects = self.findObjects()
        msg = Radar2CombatControlMsg(time, self._ID, self.cp_ID, visible_objects)
        logger.radar(f"Radar с id {self._ID} отправил сообщение CombatControlPoint с id {self.cp_ID} с видимыми объектами")
        self._sendMessage(msg)

    def changeSectorPerSec(self, new_pan_sec: float, new_tilt_sec: float):
        self.pan_per_sec = new_pan_sec
        self.tilt_per_sec = new_tilt_sec


class RadarSector(RadarRound):
    def __init__(self, dispatcher, ID: int, cp_ID: int, aero_env: AeroEnv,
                 pos, pan_start, tilt_start, dist, pan_angle, tilt_angle, pan_sec, tilt_sec, type_of_view):
        """ Класс, описывающий работу РЛС секторного обзора, является дочерним классом от РЛС кругового обзора:
         :param pan_angle: максимальный угол раскрыва по азимуту
         :param tilt_angle: максимальный угол раскрыва по углу наклона
         :param type_of_view: horizontal - соответствует рисунку а) для секторного РЛС,
                              vertical - соответствует рисунку б) для секторного РЛС
                              (см. README.md)"""
        super().__init__(dispatcher, ID, cp_ID, aero_env, pos, pan_start, tilt_start, dist, pan_sec, tilt_sec)
        self.pan_angle = pan_angle
        self.tilt_angle = tilt_angle
        self.type = type_of_view

    def moveToNextSector(self):
        if self.type == "horizontal":
            self.pan_cur = (self.pan_cur + self.pan_per_sec) % 360
            if self.pan_cur == (self.pan_start + self.pan_angle) % 360:
                self.tilt_cur = (self.tilt_cur + self.tilt_per_sec) % 180
                if self.tilt_cur == (self.tilt_start + self.tilt_angle) % 180:
                    self.tilt_cur = self.tilt_start
                self.pan_cur = self.pan_start
        elif self.type == "vertical":
            self.tilt_cur = (self.tilt_cur + self.tilt_per_sec) % 180
            if self.tilt_cur == (self.tilt_start + self.tilt_angle) % 180:
                self.pan_cur = (self.pan_cur + self.pan_per_sec) % 360
                if self.pan_cur == (self.pan_start + self.pan_angle) % 360:
                    self.pan_cur = self.pan_start
                self.tilt_cur = self.tilt_start

    def changeSector(self, new_pan: float, new_tilt: float):
        self.pan_angle = new_pan
        self.tilt_angle = new_tilt