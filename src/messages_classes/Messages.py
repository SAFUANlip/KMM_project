import numpy as np

from config.constants import MSG_RADAR2CCP_type, MSG_CCP2SD_type, \
    MSG_SD2CCP_MS_type, MSG_SD2CCP_NS_type, MSG_CCP2RADAR_type, MSG_RADAR2GM_type, MSG_RADAR2DRAWER_type, \
    MSG_CCP_MISSILE_CAPACITY_type, MSG_GM2RADAR_type, MSG_RADAR2CCP_GM_HIT_type, MSG_AEROENV2DISPATCHER_type, \
    MSG_AEROENV2DISPATCHER_VIEW_type
from src.messages_classes.BaseMessage import BaseMessage


class Radar2CombatControlMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, visible_objects: list):
        '''
        :param visible_objects: список видимых объектов из списков типа
                                [положение объекта, направление скорости объекта, модуль скорости объекта]
        '''
        super().__init__(MSG_RADAR2CCP_type, 1, time, sender_ID, receiver_ID)
        self.visible_objects = visible_objects


class Radar2DrawerMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, pos_objects: list):
        '''
        :param visible_objects: список видимых объектов из списков типа
                                [положение объекта, направление скорости объекта, модуль скорости объекта]
        '''
        super().__init__(MSG_RADAR2DRAWER_type, 1, time, sender_ID, receiver_ID)
        self.pos_objects = pos_objects


class CombatControl2StartingDeviceMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, order: int,
                 coord: np.array([float, float, float])) -> None:
        super(CombatControl2StartingDeviceMsg, self).__init__(MSG_CCP2SD_type, 1, time, sender_ID, receiver_ID)
        self.order = order
        self.coord = coord

class MissileCapacityMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, missile_number: int = 0) -> None:
        super(MissileCapacityMsg, self).__init__(MSG_CCP_MISSILE_CAPACITY_type, 1, time, sender_ID, receiver_ID)
        self.missile_number = missile_number


# ответное сообщение для пбу
class MissileStarted(BaseMessage):

    def __init__(self, time: float, sender_ID: int, receiver_ID: int, id_missile: int, order: int) -> None:
        super(MissileStarted, self).__init__(MSG_SD2CCP_MS_type, 0, time, sender_ID, receiver_ID)
        self.id_missile = id_missile
        self.order = order


class NoMissiles(BaseMessage):

    def __init__(self, time: float, sender_ID: int, receiver_ID: int, order: int) -> None:
        super(NoMissiles, self).__init__(MSG_SD2CCP_NS_type, 0, time, sender_ID, receiver_ID)
        self.order = order


class CombatControl2RadarMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int,
                 new_target_coord: np.array([float, float, float]), target_vel: np.array([float, float, float]), missile_id:int) -> None:
        """
        :param time:
        :param sender_ID:
        :param receiver_ID: ID ракеты
        :param new_target_coord: обновленные координаты цели в формате [int, int, int]
        """
        super(CombatControl2RadarMsg, self).__init__(MSG_CCP2RADAR_type, 10, time, sender_ID, receiver_ID)
        self.new_target_coord = new_target_coord
        self.target_vel = target_vel
        self.missile_id = missile_id


class Radar2MissileMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int,
                 new_target_coord: np.array([float, float, float]), target_vel: np.array([float, float, float])) -> None:
        """
        :param time:
        :param sender_ID:
        :param receiver_ID: ID ракеты
        :param new_target_coord: обновленные координаты цели в формате [int, int, int]
        """
        super(Radar2MissileMsg, self).__init__(MSG_RADAR2GM_type, 10, time, sender_ID, receiver_ID)
        self.new_target_coord = new_target_coord
        self.target_vel = target_vel


class CombatControlPoint_ViewMessage(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, view_dict) -> None:
        super(CombatControlPoint_ViewMessage, self).__init__(MSG_CCP2GUItype, 0, time, sender_ID, receiver_ID)
        self.view_dict = view_dict


class GuidedMissileHit2RadarMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int) -> None:
        super(GuidedMissileHit2RadarMsg, self).__init__(MSG_GM2RADAR_type, 0, time, sender_ID, receiver_ID)

class CombatControlPoint_InitMessage(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int) -> None:
        super(CombatControlPoint_InitMessage, self).__init__(MSG_GM2RADAR_type, 0, time, sender_ID, receiver_ID)



class GuidedMissileHit2CCPMsg(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, guided_missile_id:int) -> None:
        super(GuidedMissileHit2CCPMsg, self).__init__(MSG_RADAR2CCP_GM_HIT_type, 0, time, sender_ID, receiver_ID)
        self.guided_missile_id = guided_missile_id


class AeroEnv_InitMessage(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int) -> None:
        super(AeroEnv_InitMessage, self).__init__(MSG_AEROENV2DISPATCHER_type, 0, time, sender_ID, receiver_ID)

class AeroEnv_ViewMessage(BaseMessage):
    def __init__(self, time: float, sender_ID: int, receiver_ID: int, view_dict) -> None:
        super(AeroEnv_ViewMessage, self).__init__(MSG_AEROENV2DISPATCHER_VIEW_type, 0, time, sender_ID, receiver_ID)
        self.view_dict = view_dict