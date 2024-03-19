from src.messages.BaseMessage import BaseMessage


class Radar2CombatControlMsg(BaseMessage):
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int, visible_objects: list):
        '''
        :param visible_objects: список видимых объектов из списков типа
                                [положение объекта, направление скорости объекта, модуль скорости объекта]
        '''
        super().__init__(type, priority, time, sender_ID, receiver_ID)
        self.visible_objects = visible_objects
class CombatControl2StartingDeviceMsg(BaseMessage):
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int, message) -> None:
        super(CombatControl2StartingDeviceMsg, self).__init__(type, priority, time, sender_ID, receiver_ID)
        self.message = message

class MissileStarted(BaseMessage):

    def __init__(self, priority: int, time: int, sender_ID: int, receiver_ID: int, id_missile: int) -> None:
        super(MissileStarted, self).__init__(6001, priority, time, sender_ID, receiver_ID)
        self.id_missile = id_missile

class NoMissiles(BaseMessage):

    def __init__(self, priority: int, time: int, sender_ID: int, receiver_ID: int) -> None:
        super(NoMissiles, self).__init__(6002, priority, time, sender_ID, receiver_ID)
