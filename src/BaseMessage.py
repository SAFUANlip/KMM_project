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


class BaseMessageRadar(BaseMessage):
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int, visible_targets: list):
        super().__init__(type, priority, time, sender_ID, receiver_ID)
        self.visible_targets = visible_targets