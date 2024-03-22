from math import floor
from typing import List
from src.messages.BaseMessage import BaseMessage
from src.classes.Simulated import Simulated
from copy import deepcopy

class ModelDispatcher:
###
### Класс диспетчера моделей. Синхронизирует моделирование всех моделей и обеспечивает обмен сообщениями между моделями
###
    __objects: List[Simulated]          # Массив моделей
    __messages: List[List[BaseMessage]] # Массив сообщений, предоставляет историю сообщений
    __current_step: int                 # Текущий шаг моделирования
    __simulating_rate: float            # Количество шагов моделирования в секунду(скорость моделирования)
    __simulation_time: float            # Время моделирования конфигурации моделей

    def __init__(self) -> None:
        self.__objects = list()
        self.__messages = [list()]
        self.__current_step = 0
        self.__simulating_rate = 1
        self.__simulation_time = 100

    # Задание скорости моделирования
    # Args:
    #       rate - скорость
    #
    def setSimulatingRate(self, rate: float) -> None:
        self.__simulating_rate = rate

    # Задание времени моделирования
    # Args:
    #       time - желаемое время моделирования
    #
    def setSimulationTime(self, time: float) -> None:
        self.__simulation_time = time

    # Задание объектов моделирования
    # Args:
    #       objects - массив моделей
    #
    def configurate(self, objects: List[Simulated]) -> None:
        self.__objects = objects

    # Запуск моделирования
    def run(self) -> None:
        simulating_steps_number: int = floor(self.__simulation_time * self.__simulating_rate)
        while self.__current_step < simulating_steps_number:
            self.__messages.append(list())
            current_time: float = self.__current_step / self.__simulating_rate
            for object in self.__objects:
                object.runSimulationStep(current_time)
            self.__current_step += 1

    # Добавить сообщение в массив. 
    # ! Это сообщение будет получено, только на следующем шаге моделирования !
    # Args:
    #       msg - новое сообщение
    #
    def addMessage(self, msg: BaseMessage) -> None:
        self.__messages[self.__current_step + 1].append(msg)

    # Отдать сообщения, связанные с выбранным получателем
    # Args:
    #       receiver_ID - ID получателя. Если ID = -1, то получателеми являются все модели, кроме отправителя
    #
    def giveMessages(self, receiver_ID: int) -> List[BaseMessage]:
        return [msg for msg in self.__messages[self.__current_step] if msg.receiver_ID == receiver_ID or (msg.receiver_ID == -1 and msg.sender_ID != msg.receiver_ID)]
    
    # Отдать сообщения выбранного типа, связанные с выбранным получателем
    # Args:
    #       receiver_ID - ID получателя. Если ID = -1, то получателеми являются все модели, кроме отправителя
    #       msg_type - тип сообщения
    #
    def giveMessagesByType(self, receiver_ID: int, msg_type: int) -> List[BaseMessage]:
        return [msg for msg in self.__messages[self.__current_step] if (msg.receiver_ID == receiver_ID or (msg.receiver_ID == -1) and msg.sender_ID != msg.receiver_ID) and msg.type == msg_type]

    def getMessageHistory(self):
        return self.__simulating_rate, deepcopy(self.__messages)
