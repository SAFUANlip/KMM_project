import typing

import numpy as np

from config.constants import GuidedMissile_SPEED
from src.messages.Messages import CombatControl2StartingDeviceMsg, CombatControl2MissileMsg
from src.classes.Simulated import Simulated, ModelDispatcher

from src.utils.logger import logger
class CCTarget:
    def __init__(self, coord: np.array, speed_dir: np.array, speed_mod: float, upd_time: float) -> None:
        """
        :param coord: координата увиденной цели
        :param speed_dir: направление скорости
        :param speed_mod: модуль скорости
        :param upd_time: время, в которое произошло посл изменение класса
        """
        self.coord = coord
        self.speed_dir = speed_dir
        self.speed_mod = speed_mod
        self.upd_time = upd_time

    def upd_coord(self, new_coord: float, time: float) -> None:
        """
        Функция для обновления координаты цели
        :param new_coord: новая координата цели
        :param time: время, когда вызвали функцию
        """
        self.coord = new_coord
        self.upd_time = time

    def upd_speed_mod(self, new_speed_mod: float, time: float) -> None:
        """
        Функция для обновления модуля скорости цели
        :param new_speed_mod: новый модуль скорости цели
        :param time:  время, когда вызвали функцию
        """
        self.speed_mod = new_speed_mod
        self.upd_time = time


class CCMissile:
    def __init__(self, missile_coord, missile_id, target_coord, time):
        self.coord = missile_coord
        self.target_coord = target_coord
        self.id = missile_id
        self.speed_mod = GuidedMissile_SPEED
        self.upd_time = time

    def upd_coord(self, new_coord: float, time: float) -> None:
        """
        Функция для обновления координаты ЗУР
        :param new_coord: новая координата ЗУР
        :param time: время, когда вызвали функцию
        """
        self.coord = new_coord
        self.upd_time = time

    def upd_speed_mod(self, new_speed_mod: float, time: float) -> None:
        """
        Функция для обновления модуля скорости ЗУР
        :param new_speed_mod: новый модуль скорости ЗУР
        :param time:  время, когда вызвали функцию
        """
        self.speed_mod = new_speed_mod
        self.upd_time = time

    def upd_target_coord(self, new_target_coord: float) -> None:
        """
        Функция для обновления координаты цели, за которой летит ЗУР
        :param new_target_coord: новая координата цели ЗУР
        """
        self.target_coord = new_target_coord


class CombatControlPoint(Simulated):
    def __init__(self, dispatcher: ModelDispatcher, ID: int, StartingDevices_coords):
        super().__init__(dispatcher, ID, None)
        self.all_id = {}
        self.target_list = []
        self.missile_list = []
        self.StartingDevices_coords = StartingDevices_coords

    def find_most_similar(self, visible_object: list, cur_time: float) -> typing.Tuple[
        int, typing.Union[CCMissile, CCTarget]]:
        """

        :param visible_object:
        :return: 0 if it is a new target, else
        1 - old target
        2 - old missile

        """
        obj_coord = visible_object[0]

        min_diff = 10e10
        sim_obj = None
        obj_type = 0

        for target in self.target_list:
            target_coord = target.coord
            target_speed_mod = target.speed_mod
            last_target_time = target.upd_time

            coord_dif = (np.sum((target_coord - obj_coord) ** 2)) ** 0.5

            time_went = cur_time - last_target_time

            if (coord_dif < min_diff and max(0, target_speed_mod *
                                                (time_went - 1)) <= coord_dif
                    <= max(0, target_speed_mod * (time_went + 1))):
                min_diff = coord_dif
                obj_type = 1
                sim_obj = target

        for missile in self.missile_list:
            missile_coord = missile.coord
            missile_speed_mod = missile.speed_mod
            last_missile_time = missile.upd_time
            coord_dif = (np.sum((missile_coord - obj_coord) ** 2)) ** 0.5

            time_went = cur_time - last_missile_time
            if (coord_dif < min_diff and max(0, missile_speed_mod * (time_went - 1))
                    <= coord_dif <= max(0,
                                        missile_speed_mod * (
                                                time_went + 1))):
                min_diff = coord_dif
                obj_type = 2
                sim_obj = missile
        return obj_type, sim_obj

    def runSimulationStep(self, time: float) -> None:
        """
        :param time: текущее время
        """
        msgFromRadar = self._checkAvailableMessagesByType(2001)
        if len(msgFromRadar) == 0:
            return

        logger.combat_control(f"ПБУ получила от МФР {len(msgFromRadar[0].visible_objects)} объектов")
        if len(self.target_list) == 0:  # начало программы, когда на поле только цели
            for msg in msgFromRadar:
                visible_objects = msg.visible_objects
                for visible_object in visible_objects:
                    coord = visible_object[0]
                    speed_direct = visible_object[1]
                    speed_mod = visible_object[2]

                    self.target_list.append(CCTarget(coord, speed_direct, speed_mod, time))
                    # положить в память новые цели
                    # FIXME id of ПУ is not 2000
                    msg2StartingDevice = CombatControl2StartingDeviceMsg(time,
                                                                         self._ID, 2000, len(self.target_list) - 1,
                                                                         coord)

                    logger.combat_control("ПБУ отправила ПУ координаты новой цели")
                    self._sendMessage(msg2StartingDevice)  # сказала ПУ, что нужно запустить
                    # ЗУР по координатам coord
        else:
            # получить id  ЗУР, которые ПУ отправила
            msgsFromStartingDevice = self._checkAvailableMessagesByType(6001)

            logger.combat_control(f"ПБУ получила от ПУ {len(msgsFromStartingDevice)} сообщений")
            if len(msgsFromStartingDevice) > 0:
                if not isinstance(msgsFromStartingDevice, list):
                    msgsFromStartingDevice = [msgsFromStartingDevice]

                # дальше надо соотнести id ЗУР, координаты ЗУР и координаты их Целей
                for msgFromStartingDevice in msgsFromStartingDevice:

                    missile_id = msgFromStartingDevice.id_missile
                    startingDevice_id = msgFromStartingDevice.sender_ID
                    # missile_coord = self.StartingDevices_coords[startingDevice_id]# TODO: Богдан
                    missile_coord = self.StartingDevices_coords[startingDevice_id]

                    target_num_list = msgFromStartingDevice.order

                    target_coord = self.target_list[target_num_list].coord
                    self.missile_list.append(CCMissile(missile_coord, missile_id,
                                                       target_coord, time))
                    logger.combat_control(f"ПБУ получила от ПУ id ЗУР:{missile_id}, начальные координаты ЗУР:{missile_coord}")
                    # коорд зур, коорд ее цели, id зур, скорость зур

            # отделить новые цели от всего что было раньше
            for msg in msgFromRadar:
                visible_objects = msg.visible_objects
                for visible_object in visible_objects:
                    obj_coord = visible_object[0]
                    obj_speed_mod = visible_object[2]

                    obj_type, sim_obj = self.find_most_similar(visible_object, time)
                    if obj_type == 0:
                        # new target
                        pass

                    elif obj_type == 1:  # старая цель, надо обновить данные о ней в листах
                        # target list и missiles list и после этого ЗУР, которая летит за ней,
                        # перенаправить
                        idx = self.target_list.index(sim_obj)

                        old_target_coord = self.target_list[idx].coord

                        self.target_list[idx].upd_coord(obj_coord, time)
                        self.target_list[idx].upd_speed_mod(obj_speed_mod, time)

                        for i in range(len(self.missile_list)):
                            missile = self.missile_list[i]

                            if (missile.target_coord == old_target_coord).all():
                                self.missile_list[i].upd_target_coord(obj_coord)

                                missile_id = self.missile_list[i].id
                                msg2Missile = CombatControl2MissileMsg(time, self._ID, missile_id, obj_coord)
                                self._sendMessage(msg2Missile)

                                logger.combat_control(f"ПБУ отправила сообщение ЗУР с id:{missile_id}, новые координаты:{obj_coord}")
                                break

                    elif obj_type == 2:  # old missile, have to upd fields in missile list
                        idx = self.missile_list.index(sim_obj)
                        self.missile_list[idx].upd_coord(obj_coord, time)
                        self.missile_list[idx].upd_speed_mod(obj_speed_mod, time)



