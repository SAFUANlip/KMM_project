import numpy as np
from src.messages.Messages import Radar2CombatControlMsg
from src.classes.Simulated import Simulated
from src.classes.AeroEnv import AeroEnv


class RadarRound(Simulated):
    def __init__(self, dispatcher, ID: int, cp_ID: int, aero_env: AeroEnv,
                 pos: tuple, pan_start, tilt_start, view_distance: int,
                 pan_per_sec: float, tilt_per_sec: float):
        """ Класс, описывающий работу РЛС кругового типа обзора, является родительским классом
         для РЛС секторного типа обзора:
         :param dispatcher: ссылка на объект диспетчера
         :param ID: собственный ID
         :param cp_ID: ID ПБУ
         :param pos: координаты положения РЛС, относительно глобальной СК (x, y, z)
         :param pan_start: начальное положение по углу поворота относительно глобальной СК
         :param tilt_start: начальное положение по углу наклона относительно глобальной СК
         :param view_distance: дальность обзора РЛС
         :param pan_per_sec: угол раскрыва по углу поворота за секунду обзора
         :param tilt_per_sec: угол раскрыва по углу наклона за секунду обзора """
        super().__init__(dispatcher, ID)
        self.cp_ID = cp_ID
        self.aero_env = aero_env
        self.pos = pos
        self.pan_start = pan_start
        self.tilt_start = tilt_start  # на потом

        self.pan_cur = pan_start  # начало секундного сектора обзора в данный момент времени по углу поворота
        self.tilt_cur = tilt_start  # начало секундного сектора обзора в данный момент времени по углу наклона

        # параметры зависящие от типа рлс
        self.view_distance = view_distance
        self.pan_per_sec = pan_per_sec
        self.tilt_per_sec = tilt_per_sec

    def find_objects(self):
        all_objects = self.aero_env.getEntities()
        visible_objects = []
        for obj in all_objects:
            r = np.linalg.norm(obj.pos - self.pos)
            if r < self.view_distance:
                x, y, z = obj.pos
                tilt = np.arcsin(z/r) - self.tilt_start
                pan = np.arcsin(y/(r*np.cos(tilt))) - self.pan_start
                if self.pan_cur < pan < self.pan_cur + self.pan_per_sec and self.tilt_cur < tilt < self.tilt_cur + self.tilt_per_sec:
                    pos = obj.pos + np.random.randint(-0.001 * r, 0.001 * r, size=3)

                    speed = np.linalg.norm(obj.vel)
                    velocity_from_radar = obj.vel + np.random.randint(-0.001 * speed, 0.001 * speed, size=3)
                    speed_from_radar = np.linalg.norm(velocity_from_radar)

                    visible_objects.append([pos, velocity_from_radar, speed_from_radar])
        return visible_objects

    def move_to_next_sector(self):
        # винтовой обзор
        self.pan_cur = (self.pan_cur + self.pan_per_sec) % 360
        if self.pan_cur == self.pan_start:
            self.tilt_cur = (self.tilt_cur + self.tilt_per_sec) % 180

    def runSimulationStep(self, time: int):
        visible_objects = self.find_objects()
        msg = Radar2CombatControlMsg(time, self._ID, self.cp_ID, visible_objects)
        self._sendMessage(msg)
        self.move_to_next_sector()

    def change_sector_per_sec(self, new_pan_sec: float, new_tilt_sec: float):
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

    def move_to_next_sector(self):
        if type == "horizontal":
            self.pan_cur = (self.pan_cur + self.pan_per_sec) % 360
            if self.pan_cur == self.pan_start + self.pan_angle:
                pass

    def change_sector(self, new_pan: float, new_tilt: float):
        self.pan_angle = new_pan
        self.tilt_angle = new_tilt
