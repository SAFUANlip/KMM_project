import typing

import numpy as np

from simulation_process.constants import GuidedMissile_SPEED, MSG_RADAR2CCP_type, \
    MSG_SD2CCP_MS_type, MSG_CCP_MISSILE_CAPACITY_type, MSG_RADAR2CCP_GM_HIT_type, NEW_TARGET, OLD_TARGET, \
    OLD_GM, DISPATCHER_ID, MISSILE_TYPE_DRAWER, TARGET_TYPE_DRAWER, DRAWER_ID, ccp_rad, GuidedMissile_SPEED_MIN, \
    GuidedMissile_LifeTime, MAX_DIST_DETECTION
from simulation_process.messages_classes.Messages import CombatControl2StartingDeviceMsg, CombatControl2RadarMsg, MissileCapacityMsg, \
    CombatControlPoint_ViewMessage, CombatControlPoint_InitMessage, CombatControl2DrawerMsg
from simulation_process.modules_classes.Simulated import Simulated, ModelDispatcher
from logs.logger import logger


class CCTarget:
    def __init__(self, coord: np.array, speed_dir: np.array, speed_mod: float, upd_time: float) -> None:
        """
        :param coord: координата увиденной цели
        :param speed_dir: направление скорости
        :param speed_mod: модуль скорости
        :param upd_time: время, в которое произошло посл изменение класса
        """
        self.coord = coord
        self.seen_time = -1
        self.speed_dir = speed_dir
        self.speed_mod = speed_mod
        self.upd_time = upd_time

    def updСoord(self, new_coord: float, time: float) -> None:
        """
        Функция для обновления координаты цели
        :param new_coord: новая координата цели
        :param time: время, когда вызвали функцию
        """
        self.coord = new_coord
        self.upd_time = time

    def updSeenTime(self, time: float) -> None:
        """

        """
        self.seen_time = time
    def updSpeedMod(self, new_speed_mod: float, time: float) -> None:
        """
        Функция для обновления модуля скорости цели
        :param new_speed_mod: новый модуль скорости цели
        :param time:  время, когда вызвали функцию
        """
        self.speed_mod = new_speed_mod
        self.upd_time = time


class CCMissile:
    def __init__(self, missile_coord, missile_id, target_coord, target_vel, target_speed, time):
        self.coord = missile_coord
        self.target_coord = target_coord
        self.seen_time = -1
        self.id = missile_id
        self.speed_mod = GuidedMissile_SPEED
        self.target_speed = target_speed
        self.target_vel = target_vel
        self.upd_time = time

    def updСoord(self, new_coord: float, time: float) -> None:
        """
        Функция для обновления координаты ЗУР
        :param new_coord: новая координата ЗУР
        :param time: время, когда вызвали функцию
        """
        self.coord = new_coord
        self.upd_time = time

    def updSeenTime(self, time: float) -> None:
        """

        """
        self.seen_time = time


    def updSpeedMod(self, new_speed_mod: float, time: float) -> None:
        """
        Функция для обновления модуля скорости ЗУР
        :param new_speed_mod: новый модуль скорости ЗУР
        :param time:  время, когда вызвали функцию
        """
        self.speed_mod = new_speed_mod
        self.upd_time = time

    def updTargetCoord(self, new_target_coord: float) -> None:
        """
        Функция для обновления координаты цели, за которой летит ЗУР
        :param new_target_coord: новая координата цели ЗУР
        """
        self.target_coord = new_target_coord

    def updTargetVel(self, new_target_vel: float) -> None:
        """
        Функция для обновления вектора скорости цели, за которой летит ЗУР
        :param new_target_vel: новая координата цели ЗУР
        """
        self.target_vel = new_target_vel


class CombatControlPoint(Simulated):
    def __init__(self, dispatcher: ModelDispatcher, ID: int, starting_devices_coords: dict, radars_coords: dict):
        super().__init__(dispatcher, ID, None)
        self.target_dict = {}
        self.missile_dict = {}
        self.starting_devices_coords = starting_devices_coords
        self.radars_coords = radars_coords
        self.starting_devices_capacity = {}
        self.starting_devices_launched = {}
        self.target_order = 0
        self.missile_order = 0
        self.start = True

        logger.combat_control(f"starting_devices_coords {starting_devices_coords}")
        logger.combat_control(f"Создан ПБУ с ID {ID}")

    def findMostSimilarObject(self, visible_object: list, cur_time: float) -> typing.Tuple[
        int, typing.Union[CCMissile, CCTarget]]:
        """

        :param visible_object:
        :return: object type

        """
        obj_coord = visible_object[0]
        obj_error = abs(visible_object[-1])

        min_diff = 10e10
        sim_obj_key = None
        obj_type = NEW_TARGET

        tick = self._simulating_tick

        for key, target in self.target_dict.items():
            if target.seen_time == cur_time:
                continue
            target_coord = target.coord
            target_speed_mod = target.speed_mod
            last_target_time = target.upd_time

            coord_dif = (np.sum((target_coord - obj_coord) ** 2)) ** 0.5

            time_went = cur_time - last_target_time

            logger.combat_control(
                f"ПБУ видит объект, {max(0, target_speed_mod * (time_went - ccp_rad * tick) - obj_error)}, "
                f" {coord_dif}, {max(0, target_speed_mod * (time_went + ccp_rad * tick) + obj_error)}, "
                f"ccp rad {ccp_rad}, tick {tick}, target_speed_mod {target_speed_mod}, obj_error {obj_error},"
                f"time went {time_went}, coord_dif {coord_dif}")

            logger.combat_control(
                f"координата текущей target {target_coord}, координата текущего объекта {obj_coord}\n")

            if (coord_dif < min_diff and max(0, target_speed_mod *
                                                (time_went - ccp_rad * tick) - obj_error) <= coord_dif
                    <= max(0, target_speed_mod * (time_went + ccp_rad * tick) + obj_error)):
                min_diff = coord_dif
                obj_type = OLD_TARGET
                sim_obj_key = key

        for key, missile in self.missile_dict.items():
            if missile.seen_time == cur_time:
                continue
            missile_coord = missile.coord
            missile_speed_mod = missile.speed_mod
            last_missile_time = missile.upd_time
            coord_dif = (np.sum((missile_coord - obj_coord) ** 2)) ** 0.5

            time_went = cur_time - last_missile_time

            logger.combat_control(
                f"ПБУ видит объект, {max(0, missile_speed_mod * (time_went - ccp_rad * tick) - obj_error)}, "
                f"{coord_dif}, {max(0, missile_speed_mod * (time_went + ccp_rad * tick) + obj_error)}, "
                f"ccp rad {ccp_rad}, tick {tick}, target_speed_mod {missile_speed_mod}, obj_error {obj_error}, "
                f"time went {time_went}, coord_dif {coord_dif}")

            logger.combat_control(
                f"координата текущей зур {missile_coord}, координата текущего объекта {obj_coord}\n")

            if (coord_dif < min_diff and max(0, missile_speed_mod * (time_went - ccp_rad * tick) - obj_error)
                    <= coord_dif <= max(0,
                                        missile_speed_mod * (time_went + ccp_rad * tick) + obj_error)):
                min_diff = coord_dif
                obj_type = OLD_GM
                sim_obj_key = key

        if obj_type == 2:
            self.missile_dict[sim_obj_key].updSeenTime(cur_time)
            logger.combat_control(
                f"ПБУ обновила SeenTime у зур с id {self.missile_dict[sim_obj_key].id}, координатами {self.missile_dict[sim_obj_key].coord}")
        if obj_type == 1:
            self.target_dict[sim_obj_key].updSeenTime(cur_time)
            logger.combat_control(
                f"ПБУ обновила SeenTime у цели с id {self.target_dict[sim_obj_key]}, координатами ")

        logger.combat_control(
            f"ПБУ решила что объект с координатами {obj_coord} это {obj_type}, ЗУР - 2, Цель старая - 1, Цель новая - 0")
        return obj_type, sim_obj_key

    def request_starting_devices_capacities(self, time: float) -> None:
        for key in self.starting_devices_coords.keys():
            self.starting_devices_launched[key] = 0
            self.starting_devices_capacity[key] = 0

            msg2starting_device = MissileCapacityMsg(time, self._ID, key)
            self._sendMessage(msg2starting_device)  # спрашиваю ПУ, сколько у них ЗУР в запасе
            logger.combat_control(f"ПБУ спросила ПУ с id {key} сколько у нее ЗУР")

    def delete_missile(self, missile_id: int):
        to_del = []
        target_coord = None

        # нужно удалить ракету и цель, за которой она следила из обоих списков
        for key, missile in self.missile_dict.items():
            if missile.id == missile_id:
                target_coord = missile.target_coord
                to_del.append(key)
                break

        for key in to_del:
            self.missile_dict.pop(key, None)

        to_del = []
        for key, target in self.target_dict.items():
            if (target.coord == target_coord).all():
                to_del.append(key)
                break

        for key in to_del:
            self.target_dict.pop(key, None)

    def get_starting_devices_capacity(self):
        missile_capacity_msg = self._checkAvailableMessagesByType(MSG_CCP_MISSILE_CAPACITY_type)
        if len(missile_capacity_msg) != 0:
            logger.combat_control(f"ПБУ получил от ПУ {len(missile_capacity_msg)} сообщений о кол-ве ЗУР")

            for msg in missile_capacity_msg:
                self.starting_devices_capacity[msg.sender_ID] = msg.missile_number
                logger.combat_control(f"ПБУ получил от ПУ {msg.sender_ID} сообщений о {msg.missile_number} ЗУР")

    def get_hit_guided_missiles(self):
        msgs_missile_hit = self._checkAvailableMessagesByType(MSG_RADAR2CCP_GM_HIT_type)

        if len(msgs_missile_hit) != 0:
            logger.combat_control(
                f"ПБУ получил {len(msgs_missile_hit)} сообщений от Радара о том что ЗУР перестала существовать ")

            for msg in msgs_missile_hit:
                hit_guided_missile_id = msg.guided_missile_id
                self.delete_missile(hit_guided_missile_id)

    def get_launched_missiles(self, time):
        msgsFromStartingDevice = self._checkAvailableMessagesByType(MSG_SD2CCP_MS_type)
        logger.combat_control(f"ПБУ получил от ПУ {len(msgsFromStartingDevice)} сообщений о запуске ЗУР")
        if len(msgsFromStartingDevice) > 0:
            if not isinstance(msgsFromStartingDevice, list):
                msgsFromStartingDevice = [msgsFromStartingDevice]

            # дальше надо соотнести id ЗУР, координаты ЗУР и координаты их Целей
            for msgFromStartingDevice in msgsFromStartingDevice:
                missile_id = msgFromStartingDevice.id_missile
                startingDevice_id = msgFromStartingDevice.sender_ID
                missile_coord = self.starting_devices_coords[startingDevice_id]

                target_num_dict = msgFromStartingDevice.order
                logger.combat_control(f"{target_num_dict}, {len(self.target_dict.items())}")

                target_coord = self.target_dict[target_num_dict].coord
                target_speed = self.target_dict[target_num_dict].speed_mod
                target_vel = self.target_dict[target_num_dict].speed_dir

                self.missile_order = self.missile_order + 1
                self.missile_dict[self.missile_order] = CCMissile(missile_coord, missile_id,
                                                                  target_coord, target_vel, target_speed, time)
                logger.combat_control(
                    f"ПБУ получил от ПУ id ЗУР:{missile_id}, начальные координаты ЗУР:{missile_coord}")
                # коорд зур, коорд ее цели, id зур, скорость зур

    def send_vis_objects2gui(self, time):
        missile_list = []
        target_list = []
        view_dict = {}

        for key, missile in self.missile_dict.items():
            coord = missile.coord
            id = missile.id
            missile_list.append([time, id, coord])

        for key, target in self.target_dict.items():
            coord = target.coord
            target_list.append([time, coord])

        view_dict["missiles"] = missile_list
        view_dict["targets"] = target_list

        msg2drawer = CombatControlPoint_ViewMessage(
            time=time,
            sender_ID=self._ID,
            receiver_ID=DISPATCHER_ID,
            view_dict=view_dict,
        )
        self._sendMessage(msg2drawer)
        logger.combat_control(f"ПБУ отправил {len(target_list) + len(missile_list)} смс GUI")

    def send_vis_objects2drawer(self, time):
        list_for_drawer = []

        for key, missile in self.missile_dict.items():
            coord = missile.coord
            list_for_drawer.append([MISSILE_TYPE_DRAWER, coord])

        for key, target in self.target_dict.items():
            coord = target.coord
            list_for_drawer.append([TARGET_TYPE_DRAWER, coord])

        msg2drawer = CombatControl2DrawerMsg(
            time=time,
            sender_ID=self._ID,
            receiver_ID=DRAWER_ID,
            coordinates=list_for_drawer,
        )
        self._sendMessage(msg2drawer)
        logger.combat_control(f"ПБУ отправил {len(list_for_drawer)} смс Рисовальщику")

    def send_target_coords2gm_through_radar(self, gm_new_target_coords, time):
        for missile_id in gm_new_target_coords.keys():
            dist_radar2missile, radar_id, target_coord, target_vel = gm_new_target_coords[missile_id]
            msg2radar = CombatControl2RadarMsg(time, self._ID, radar_id, target_coord, target_vel,
                                               missile_id)
            self._sendMessage(msg2radar)

            logger.combat_control(
                f"ПБУ отправил сообщение Радару {radar_id}, что у ЗУР с id:{missile_id}, новые координаты ее цели:{target_coord}")

    def runSimulationStep(self, time: float) -> None:
        """
        :param time: текущее время
        """
        self.get_hit_guided_missiles()

        if self.start:
            init_msg = CombatControlPoint_InitMessage(time=time,
                                                      sender_ID=self._ID,
                                                      receiver_ID=DISPATCHER_ID)
            self._sendMessage(init_msg)

            self.request_starting_devices_capacities(time)
            self.start = False

        self.get_starting_devices_capacity()
        self.get_launched_missiles(time)

        msg_from_radar = self._checkAvailableMessagesByType(MSG_RADAR2CCP_type)
        logger.combat_control(f"ПБУ получил сообщения от {len(msg_from_radar)} МФР")


        gm_new_target_coords = {}

        if len(msg_from_radar) != 0:

            for key in self.missile_dict.keys():
                self.missile_dict[key].updSeenTime(-1)
            for key in self.target_dict.keys():
                self.target_dict[key].updSeenTime(-1)

            # отделить новые цели от всего что было раньше
            for msg in msg_from_radar:
                logger.combat_control(f"ПБУ получил {len(msg.visible_objects)}, {msg.visible_objects} сообщений от МФР с id {msg.sender_ID}")
                radar_id = msg.sender_ID

                visible_objects = msg.visible_objects
                for visible_object in visible_objects:
                    obj_coord = visible_object[0]
                    obj_speed_direct = visible_object[1]
                    obj_speed_mod = visible_object[2]

                    obj_type, sim_obj_key = self.findMostSimilarObject(visible_object, time)
                    if obj_type == NEW_TARGET:
                        # положить в память новые цели
                        min_dist = 10e10
                        sd_id = None
                        for key in self.starting_devices_coords.keys():
                            if self.starting_devices_launched[key] < self.starting_devices_capacity[key]:
                                sd_pos = self.starting_devices_coords[key]
                                dist = (np.sum((sd_pos - obj_coord) ** 2)) ** 0.5
                                if dist < min_dist:
                                    sd_id = key
                                    min_dist = dist

                        if min_dist < GuidedMissile_SPEED_MIN * GuidedMissile_LifeTime:

                            if sd_id is not None:
                                self.target_order = self.target_order + 1
                                self.target_dict[self.target_order] = CCTarget(obj_coord, obj_speed_direct,
                                                                               obj_speed_mod, time)

                                msg2StartingDevice = CombatControl2StartingDeviceMsg(time,
                                                                                     self._ID, sd_id, self.target_order,
                                                                                     obj_coord, radar_id)

                                logger.combat_control(f"ПБУ отправил ПУ id {sd_id} координаты новой цели: {obj_coord}")
                                self.starting_devices_launched[key] = self.starting_devices_launched[key] + 1
                                self._sendMessage(msg2StartingDevice)  # сказала ПУ, что нужно запустить
                            else:
                                logger.warning(f"Не осталось свободных ЗУР!!!")

                        else:
                            logger.warning(f"ЗУР не успеет долететь до цели")

                        # ЗУР по координатам coord

                    elif obj_type == OLD_TARGET:  # старая цель, надо обновить данные о ней в листах
                        # target list и missiles list и после этого ЗУР, которая летит за ней,
                        # перенаправить

                        old_target_coord = self.target_dict[sim_obj_key].coord

                        self.target_dict[sim_obj_key].updСoord(obj_coord, time)
                        self.target_dict[sim_obj_key].updSpeedMod(obj_speed_mod, time)

                        for key in self.missile_dict.keys():
                            missile = self.missile_dict[key]

                            if (missile.target_coord == old_target_coord).all():
                                self.missile_dict[key].updTargetCoord(obj_coord)
                                self.missile_dict[key].updTargetVel(obj_speed_direct)

                                missile_id = self.missile_dict[key].id
                                missile_coord = self.missile_dict[key].coord
                                target_vel = self.missile_dict[key].target_vel
                                target_coord = self.missile_dict[key].target_coord
                                dist_radar2missile = np.linalg.norm(self.radars_coords[radar_id] - missile_coord)

                                if dist_radar2missile < MAX_DIST_DETECTION:
                                    if not missile_id in gm_new_target_coords.keys():
                                        gm_new_target_coords[missile_id] = [dist_radar2missile, radar_id, target_coord, target_vel]
                                        logger.combat_control(
                                            f"инфу о ЗУР с id {missile_id} ПБУ передал Радару с id {radar_id}, расст от него до ЗУР = {dist_radar2missile}")

                                    else:
                                        old_radar2missile_dist = gm_new_target_coords[missile_id][0]
                                        if dist_radar2missile < old_radar2missile_dist:
                                            gm_new_target_coords[missile_id] = [dist_radar2missile, radar_id,
                                                                                target_coord, target_vel]

                                            logger.combat_control(
                                                f"инфу о ЗУР с id {missile_id} ПБУ передал Радару с id {radar_id}, расст от него до ЗУР = {dist_radar2missile}")


                                break

                    elif obj_type == OLD_GM:  # старая ЗУР, нужно обновить поля в листе ЗУР
                        logger.combat_control(
                            f"ПБУ увидел старую ЗУР с id:{self.missile_dict[sim_obj_key].id}, новые координаты:{obj_coord}")

                        self.missile_dict[sim_obj_key].updСoord(obj_coord, time)
                        self.missile_dict[sim_obj_key].updSpeedMod(obj_speed_mod, time)

        self.send_target_coords2gm_through_radar(gm_new_target_coords, time)
        self.send_vis_objects2gui(time)
