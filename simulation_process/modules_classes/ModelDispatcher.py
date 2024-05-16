from math import floor
from typing import List
from simulation_process.messages_classes.BaseMessage import BaseMessage
from simulation_process.modules_classes.Simulated import Simulated
from copy import deepcopy

from logs.logger import logger

from PyQt5.QtCore import QObject, pyqtSignal

class ModelDispatcher(QObject):
    """ Класс диспетчера моделей. Синхронизирует моделирование всех моделей
    и обеспечивает обмен сообщениями между моделями
    :atrib __objects: массив моделей
    :atrib __messages: массив сообщений, предоставляет историю сообщений
    :atrib __current_step: текущий шаг моделирования
    :atrib __simulating_rate: количество шагов моделирования в секунду(скорость моделирования)
    :atrib __simulation_time: время моделирования конфигурации моделей
    """
    
    tick = pyqtSignal(int)

    def __init__(self, objects: List[Simulated] = list(),
                 simulating_rate: float = 1, simulation_time: float = 100) -> None:
        """ Класс диспетчера моделей
        :param objects: массив моделей
        :param simulating_rate: количество шагов моделирования в секунду(скорость моделирования)
        :param simulation_time: время моделирования конфигурации моделей
        """
        super(ModelDispatcher, self).__init__()
        self.__objects = objects
        self.__simulating_rate = simulating_rate
        self.__simulation_time = simulation_time
        self.__messages: List[List[BaseMessage]] = [list()]
        self.__current_step: int = 0
        self.__is_running = True

    def setSimulatingRate(self, rate: float) -> None:
        """ Задание скорости моделирования
         :param rate: количество шагов моделирования в секунду(скорость моделирования)
        """
        self.__simulating_rate = rate

    def getSimulatingTick(self) -> float:
        """ Отдать время протекающее за одну итерацию моделирования
        :return: время за тик моделирования
        """
        return 1 / self.__simulating_rate

    def setSimulationTime(self, time: float) -> None:
        """ Задание времени моделирования
        :param time: желаемое время моделирования
        """
        self.__simulation_time = time

    def configurate(self, objects: List[Simulated]) -> None:
        """ Задание объектов моделирования
        :param objects: массив моделей
        """
        self.__objects = objects

    def run(self) -> None:
        """ Запуск моделирования)) """
        simulating_steps_number = floor(self.__simulation_time * self.__simulating_rate)
        while self.__current_step < simulating_steps_number and self.__is_running:
            logger.info("\n")
            logger.info(f"Номер текущего шага: {self.__current_step}")
            self.__messages.append(list())
            current_time = self.__current_step / self.__simulating_rate
            for object in self.__objects:
                object.runSimulationStep(current_time)
            self.__current_step += 1
            self.tick.emit(self.__current_step)

    def stop(self):
        self.__is_running = False

    def addMessage(self, msg: BaseMessage) -> None:
        """ Добавить сообщение в массив
        ! Это сообщение будет получено, только на следующем шаге моделирования !
        :param msg: новое сообщение
        """
        self.__messages[self.__current_step + 1].append(msg)

    def giveMessages(self, receiver_ID: int) -> List[BaseMessage]:
        """ Отдать сообщения, связанные с выбранным получателем
        :param receiver_ID: ID получателя. Если ID = -1, то получателеми являются все модели, кроме отправителя
        :return: список сообщений, отправленных получателю на предыдущей итерации моделирования
        """
        return [msg for msg in self.__messages[self.__current_step] if
                msg.receiver_ID == receiver_ID or (msg.receiver_ID == -1 and msg.sender_ID != msg.receiver_ID)]

    def giveMessagesByType(self, receiver_ID: int, msg_type: int) -> List[BaseMessage]:
        """ Отдать сообщения выбранного типа, связанные с выбранным получателем
        :param receiver_ID: ID получателя. Если ID = -1, то получателеми являются все модели, кроме отправителя
        :param msg_type: тип сообщения
        :return: список сообщений выбранного типа, отправленных получателю на предыдущей итерации моделирования
        """
        return [msg for msg in self.__messages[self.__current_step] if (msg.receiver_ID == receiver_ID or (
                    msg.receiver_ID == -1) and msg.sender_ID != msg.receiver_ID) and msg.type == msg_type]

    def getMessageHistory(self):
        """ Отдать скорость моделирования и историю сообщений
        :return: количество шагов моделирования в секунду; массив сообщений, разделённый по итерациям
        """
        return self.__simulating_rate, deepcopy(self.__messages)

