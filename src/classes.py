import numpy as np
from AeroEnv import Airplane
from Simulated import Simulated
from BaseMessage import BaseMessageRadar


class RadarRound(Simulated):
    def __init__(self, dispatcher, ID: int, coordinates: tuple, pan_start, tilt_start, view_distance: int, pan_per_sec: float, tilt_per_sec: float, pan_cur: float, tilt_cur: float):
        """ Класс, описывающий работу РЛС кругового типа обзора, является родительским классом
         для РЛС секторного типа обзора:
         :param coordinates: координаты положения РЛС, относительно глобальной СК (x, y, z)
         :param pan_start: начальное положение по углу поворота относительно глобальной СК
         :param tilt_start: начальное положение по углу наклона относительно глобальной СК
         :param view_distance: дальность обзора РЛС
         :param pan_per_sec: угол раскрыва по углу поворота за секунду обзора
         :param tilt_per_sec: угол раскрыва по углу наклона за секунду обзора
         :param pan_cur: начало секундного сектора обзора в данный момент времени по углу поворота
         :param tilt_cur: начало секундного сектора обзора в данный момент времени по углу наклона"""
        super().__init__(dispatcher, ID)

        self.coordinates = coordinates
        self.pan_start = pan_start
        self.tilt_start = tilt_start
        self.view_distance = view_distance
        self.pan_per_sec = pan_per_sec
        self.tilt_per_sec = tilt_per_sec
        self.pan_cur = pan_cur
        self.tilt_cur = tilt_cur

    def find_aims(self):
        all_aims = self._checkAvailableMessages()
        visible_aims = []
        for aim in all_aims:
            r = np.linalg.norm(aim.pos - self.coordinates)
            if r < self.view_distance:
                xa, ya, za, = aim.pos
                tilt_aim = np.arcsin(za/r) - self.tilt_start
                pan_aim = np.arcsin(ya/(r*np.cos(tilt_aim))) - self.pan_start
                if self.pan_cur < pan_aim < self.pan_cur + self.pan_per_sec and self.tilt_cur < tilt_aim < self.tilt_cur + self.tilt_per_sec:
                    visible_aims.append(aim)
        return visible_aims

    def runSimulationStep(self, time: int):
        visible_aims = self.find_aims()
        msg = BaseMessageRadar(2000, 1, time, self._ID, 1000, visible_aims)
        self._sendMessage(msg)

    def change_sector_per_sec(self, new_pan_sec: float, new_tilt_sec: float):
        self.pan_per_sec = new_pan_sec
        self.tilt_per_sec = new_tilt_sec


class RadarSector(RadarRound):
    def __init__(self, coords, dist, pan_angle, tilt_angle, pan_sec, tilt_sec, pan_cur, tilt_cur):
        """ Класс, описывающий работу РЛС секторного обзора, является дочерним классом от РЛС кругового обзора:
         :param pan_angle: максимальный угол раскрыва по азимуту
         :param tilt_angle: максимальный угол раскрыва по углу наклона"""
        super().__init__(coords, dist, pan_sec, tilt_sec, pan_cur, tilt_cur)
        self.pan_angle = pan_angle
        self.tilt_angle = tilt_angle

    def change_sector(self, new_pan: float, new_tilt: float):
        self.pan_angle = new_pan
        self.tilt_angle = new_tilt
