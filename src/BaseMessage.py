from abc import ABCMeta, abstractmethod

class BaseMessage(metaclass=ABCMeta):
#
# Базовый класс сообщения
#
    type: int        # ID класса сообщения
    priority: int    # Приоритет сообщения(Больше -> выше приоритет)
    time: int        # Время отправления сообщения
    sender_ID: int   # ID модели отправителя
    receiver_ID: int # ID модели получателя

    @abstractmethod
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int) -> None:
        self.type = type
        self.priority = priority
        self.time = time
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID


class Radar2CombatControlMsg(BaseMessage):
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int, visible_objects: list):
        '''
        :param visible_objects: список видимых объектов из списков типа
                                [положение объекта, направление скорости объекта, модуль скорости объекта]
        '''
        super().__init__(type, priority, time, sender_ID, receiver_ID)
        self.visible_objects = visible_objects