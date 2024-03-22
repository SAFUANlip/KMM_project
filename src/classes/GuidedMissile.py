import numpy as np

from src.classes.ModelDispatcher import ModelDispatcher, Simulated
from src.messages.BaseMessage import BaseMessage


class GuidedMissile(Simulated):
    def __init__(self, dispatcher: ModelDispatcher, ID: int,
                 x, y, z, speed=1200, life_time=1200, expl_radius=30) -> None:
        """

        :param dispatcher: диспетчер, для синхронизации с другими модулями
        :param ID: ID этой ракеты
        :param x:
        :param y:
        :param z:
        :param speed:
        :param life_time: возможное время жизни ракеты
        :param expl_radius: радиус взрыва ракеты
        """
        super(GuidedMissile, self).__init__(dispatcher, ID)
        self.x = x
        self.y = y
        self.z = z
        self.speed = speed
        self.life_time = life_time
        self.expl_radius = expl_radius
        self.x_target = None
        self.y_target = None
        self.z_target = None
        self.__status = 0
        self.launch_time = None
        self.__previous_time = None

    def launch(self, x_target, y_target, z_target, launch_time) -> None:
        """
        :param x_target:
        :param y_target:
        :param z_target:
        :param launch_time: время запуска
        """
        self.x_target = x_target
        self.y_target = y_target
        self.z_target = z_target
        self.launch_time = launch_time
        self.__previous_time = launch_time
        self.__status = 1

    def updateTarget(self, x_target, y_target, z_target) -> None:
        """
        Обновление координат цели
        :param x_target:
        :param y_target:
        :param z_target:
        """
        self.x_target = x_target
        self.y_target = y_target
        self.z_target = z_target

    def updateCoordinate(self, time: int) -> None:
        """
        Обновление координат ракеты
        :param time: сколько времени ракета летела с прошлого обновления координат
        """
        direction = np.array([self.x_target - self.x, self.y_target - self.y, self.z_target - self.z])
        direction = direction / np.linalg.norm(direction)
        self.x += direction[0] * self.speed * time
        self.y += direction[1] * self.speed * time
        self.z += direction[2] * self.speed * time

    def checkIsHit(self):
        """
        Проверка поражена ли цель
        """
        if ((self.x-self.x_target)**2 + (self.y-self.y_target)**2 + (self.z-self.z_target)**2)**0.5 < self.expl_radius:
            self.__status = 2
        print(f"distance to target {((self.x-self.x_target)**2 + (self.y-self.y_target)**2 + (self.z-self.z_target)**2)**0.5}")

    def getStatus(self):
        """
        Узнать статус ракеты
        0 - не активна
        1 - летит
        2 - поразила цель
        3 - пропустила цель, закончилось топливо
        :return:
        """
        return self.__status

    def runSimulationStep(self, time):
        """
        Шаг симуляции ракеты
        msg_type = 1001, сообщения корректирующие положение цели
        :param time: текущее время в симуляции
        """
        messages = self._checkAvailableMessagesByType(msg_type=3002)
        messages.sort(key=lambda x: x.priority, reverse=True)

        x_target, y_target, z_target = self.x_target, self.y_target, self.z_target

        if len(messages) != 0:
            x_target, y_target, z_target = messages[0].new_target_coord

        if self.__status == 1:
            self.updateTarget(x_target, y_target, z_target)
            self.updateCoordinate(time - self.__previous_time)
            self.checkIsHit()
            if self.__status == 2:
                print(f"HIT Target: {x_target}, {y_target}, {z_target}, is hit by Rocket with ID {self._ID}")
            elif time - self.launch_time > self.life_time:
                self.__status = 3
                print(f"MISS Target: {x_target}, {y_target}, {z_target}, is miss, Rocket with ID {self._ID} fell")

        if self.__status > 1:
            print(f"Rocket with ID {self._ID} was destroyed, with status: {self.__status}")

        self.__previous_time = time
        #print(f"ID: {self._ID}, Rokcet coordinate {self.x}, {self.y}, {self.z}")

