from abc import ABCMeta, abstractmethod
from typing import List
from src.messages.BaseMessage import BaseMessage

# Затычка против зацикливания импорта
# Импорт модуля диспетчера должен быть в конце
class ModelDispatcher:
    pass


class Simulated(metaclass=ABCMeta):
#
# Базовый класс моделей, реализует обмен сообщениями
#
    __dispatcher: ModelDispatcher # Диспетчер моделей
    _ID: int                      # ID объекта моделирования

    @abstractmethod
    def __init__(self, dispatcher: ModelDispatcher, ID: int) -> None:
        self.__dispatcher = dispatcher
        self._ID = ID
        self._simulating_tick = dispatcher.getSimulatingTick()

    # Сделать шаг моделирования
    # ! Должен быть переопределён дочерним классом !
    # Args:
    #       time - время на текущем шаге моделирования
    #
    @abstractmethod
    def runSimulationStep(self, time: int) -> None:
        pass

    # Отправить сконфигурированное сообщение
    # ! Сообщение будет получено на следующем шаге моделирования !
    # Args:
    #       msg - отправляемое сообщение
    #
    def _sendMessage(self, msg: BaseMessage) -> None:
        self.__dispatcher.addMessage(msg)

    # Получить сообщения, отправленные этому объекту
    def _checkAvailableMessages(self) -> List[BaseMessage]:
        return self.__dispatcher.giveMessages(self._ID)

    # Получить сообщения определенного типа, отправленные этому объекту
    def _checkAvailableMessagesByType(self, msg_type: int) -> List[BaseMessage]:
        return self.__dispatcher.giveMessagesByType(self._ID, msg_type)
