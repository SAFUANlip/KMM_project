from abc import ABCMeta, abstractmethod

class BaseMessage(metaclass=ABCMeta):
    """ Базовый класс сообщения, от которого наследуются все сообщения
    :atrib type: ID класса сообщения
    :atrib priority: приоритет сообщения(Больше -> выше приоритет)
    :atrib time: время отправления сообщения
    :atrib sender_ID: ID модели отправителя
    :atrib receiver_ID: ID модели получателя
    """

    @abstractmethod
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int) -> None:
        """ Базовое сообщение
        :param type: ID класса сообщения
        :param priority: приоритет сообщения(Больше -> выше приоритет)
        :param time: время отправления сообщения
        :param sender_ID: ID модели отправителя
        :param receiver_ID: ID модели получателя
        """
        self.type = type
        self.priority = priority
        self.time = time
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID