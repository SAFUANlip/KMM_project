import numpy as np
from abc import ABCMeta, abstractmethod
from typing import List
from src.messages.BaseMessage import BaseMessage

# Затычка против зацикливания импорта
# Импорт модуля диспетчера должен быть в конце
class ModelDispatcher:
    pass


class Simulated(metaclass=ABCMeta):
    """ Базовый класс моделей, реализует обмен сообщениями 
    :atrib __dispatcher: диспетчер моделей
    :atrib _ID: ID объекта моделирования
    :atrib _simulating_tick: время за тик моделирования
    """

    @abstractmethod
    def __init__(self, dispatcher: ModelDispatcher, ID: int, pos: np.array) -> None:
        """ Базовый класс моделей, реализует обмен сообщениями 
        :param dispatcher: диспетчер моделей
        :param ID: ID объекта моделирования
        """
        self.__dispatcher = dispatcher
        self._ID = ID
        self._simulating_tick: float = dispatcher.getSimulatingTick()
        self.pos = pos

    @abstractmethod
    def runSimulationStep(self, time: float) -> None:
        """ Сделать шаг моделирования
        ! Должен быть переопределён дочерним классом !
        :param time: время на текущем шаге моделирования
        """
        pass

    def _sendMessage(self, msg: BaseMessage) -> None:
        """ Отправить сконфигурированное сообщение
        ! Сообщение будет получено на следующем шаге моделирования !
        :param msg: отправляемое сообщение
        """
        self.__dispatcher.addMessage(msg)

    def _checkAvailableMessages(self) -> List[BaseMessage]:
        """ Получить сообщения, отправленные этому объекту 
        :return: список сообщений, отправленных этому объекту на предыдущей итерации моделирования
        """
        return self.__dispatcher.giveMessages(self._ID)

    def _checkAvailableMessagesByType(self, msg_type: int) -> List[BaseMessage]:
        """ Получить сообщения определенного типа, отправленные этому объекту 
        "return: список сообщений выбранного типа, отправленных этому объекту на предыдущей итерации моделирования
        """
        return self.__dispatcher.giveMessagesByType(self._ID, msg_type)
