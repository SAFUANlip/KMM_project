from typing import List

import numpy as np

from src.messages.BaseMessage import BaseMessage


class Radar2CombatControlMsg(BaseMessage):
    def __init__(self, time: int, sender_ID: int, receiver_ID: int, visible_objects: list):
        '''
        :param visible_objects: список видимых объектов из списков типа
                                [положение объекта, направление скорости объекта, модуль скорости объекта]
        '''
        super().__init__(2001, 1, time, sender_ID, receiver_ID)
        self.visible_objects = visible_objects

class CombatControl2StartingDeviceMsg(BaseMessage):
    def __init__(self, time: int, sender_ID: int, receiver_ID: int, order: int, coord: np.array) -> None:
        super(CombatControl2StartingDeviceMsg, self).__init__(3001, 1, time, sender_ID, receiver_ID)
        self.order = order
        self.coord = coord

#ответное сообщение для пбу
class MissileStarted(BaseMessage):

    def __init__(self, time: int, sender_ID: int, receiver_ID: int, id_missile: int, order: int) -> None:
        super(MissileStarted, self).__init__(6001, 0, time, sender_ID, receiver_ID)
        self.id_missile = id_missile
        self.order = order

class NoMissiles(BaseMessage):

    def __init__(self, time: int, sender_ID: int, receiver_ID: int, order: int) -> None:
        super(NoMissiles, self).__init__(6002, 0, time, sender_ID, receiver_ID)
        self.order = order

class UpdateCoordinateMSG(BaseMessage):
    def __init__(self, time: int, sender_ID: int, receiver_ID: int, new_target_coord: List[int]) -> None:
        """
        :param time:
        :param sender_ID:
        :param receiver_ID: ID ракеты
        :param new_target_coord: обновленные координаты цели в формате [int, int, int]
        """
        super(UpdateCoordinateMSG, self).__init__(3002, 10, time, sender_ID, receiver_ID)
        self.new_target_coord = new_target_coord