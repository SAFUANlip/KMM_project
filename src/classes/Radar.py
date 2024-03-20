import numpy as np
from src.messages.Messages import Radar2CombatControlMsg
from src.classes.Simulated import Simulated
from src.classes.AeroEnv import AeroEnv
from config.constants import SPEED_GuidedMissile, MAX_DIST_ERROR

class RadarRound(Simulated):
    def __init__(self, dispatcher, ID: int, cp_ID: int, aero_env: AeroEnv,
                 coordinates: tuple, pan_start, tilt_start, view_distance: int,
                 pan_per_sec: float, tilt_per_sec: float, pan_cur: float,
                 tilt_cur: float):
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
        self.cp_ID = cp_ID
        self.aero_env = aero_env
        self.coordinates = coordinates
        self.pan_start = pan_start
        self.tilt_start = tilt_start
        self.view_distance = view_distance
        self.pan_per_sec = pan_per_sec
        self.tilt_per_sec = tilt_per_sec
        self.pan_cur = pan_cur
        self.tilt_cur = tilt_cur

    def find_objects(self):
        all_objects = self.aero_env.getEntities()
        visible_objects = []
        for obj in all_objects:
            r = np.linalg.norm(np.array([obj.x, obj.y, obj.z]) - self.coordinates) #FIXME: pos? x y z?
            if r < self.view_distance:
                x, y, z = obj.x, obj.y, obj.z
                tilt = np.arcsin(z/r) - self.tilt_start
                pan = np.arcsin(y/(r*np.cos(tilt))) - self.pan_start
                if self.pan_cur < pan < self.pan_cur + self.pan_per_sec and self.tilt_cur < tilt < self.tilt_cur + self.tilt_per_sec:
                    pos = np.array([obj.x, obj.y, obj.z]) + np.random.randint(-MAX_DIST_ERROR, MAX_DIST_ERROR, size=3)
                    speed_direction = obj.vel + np.random.randint(-0.001*SPEED_GuidedMissile, 0.001*SPEED_GuidedMissile, size=3)
                    speed_modul = np.linalg.norm(speed_direction)
                    visible_objects.append([pos, speed_direction, speed_modul])
        return visible_objects

    def runSimulationStep(self, time: int):
        visible_objects = self.find_objects()
        msg = Radar2CombatControlMsg(time, self._ID, self.cp_ID, visible_objects)
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
