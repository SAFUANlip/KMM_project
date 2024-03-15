from src.Simulated import Simulated
from src.BaseMessage import BaseMessage

NUMBER_OF_MISSILES = 50
# имитация классов цели и ЗУР
class GuidedMissile:
    # 0 - не запущено, 1 - летит, 2 - попала и убилась, 3 - пролетела и не попала

    def __init__(self, x: int, y: int, z: int, id: int, status: int = 0) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.status = status    # 0 - не запущено, 1 - летит, 2 - убилась

    def start(self, x: int, y: int, z: int, status: int = 1):
        self.x_aim = x
        self.y_aim = y
        self.z_aim = z
        self.status = status

    def getStatus(self) -> int:
        pass

    def newLocation(self, x, y, z):
        pass


#ответное сообщение для пбу
class MissileStarted(BaseMessage):

    def __init__(self, priority: int, time: int, sender_ID: int, receiver_ID: int, id_missile: int) -> None:
        super(MissileStarted, self).__init__(6001, priority, time, sender_ID, receiver_ID)
        self.id_missile = id_missile

class NoMissiles(BaseMessage):

    def __init__(self, priority: int, time: int, sender_ID: int, receiver_ID: int) -> None:
        super(NoMissiles, self).__init__(6002, priority, time, sender_ID, receiver_ID)

# класс ПУ
class StartingDevice(Simulated):

    ID: int  #id пу
    missiles: list # список имеющихся зур
    # координаты пу
    x: int
    y: int
    z: int

    def __init__(self, ID: int, x: int, y: int, z: int, missiles: list) -> None:
        super().__init__(ID=ID)
        self.x = x
        self.y = y
        self.z = z
        self.missiles = [GuidedMissile(self.x, self.y, self.z, self.ID * 1000 + i) for i in range(NUMBER_OF_MISSILES)]

    # проверяем статусы зур, заполняем список убивших цель и неактивных
    def checkMissiles(self) -> tuple(list[int], list[int]):
        free_missiles = []
        killed_missiles = []

        for i in range(len(self.missiles)):
            status = self.missiles[i].getStatus()
            if (status == 0):
                free_missiles.append(i)
            elif (status == 2):
                killed_missiles.append(i)

        return tuple(free_missiles, killed_missiles)


    def runSimulationStep(self, time: float) -> None:
        # узнаём статус всех зур
        free_missiles, killed_missiles = self.checkMissiles()
        # проверяем почту на наличие сообщений от пбу и запускаем ракеты
        new_messages = Simulated._checkAvailableMessagesByType(msg_type = 3001)
        for msg in new_messages:
            # проверка наличия свободных зур
            if (len(free_missiles) == 0):
                # если нет - сигналим
                Simulated._sendMessage(NoMissiles(msg.priority, msg.time, self.ID, msg.sender_ID)) # если нет - сигналим
            else:
                # если есть - запускаем
                self.missiles[free_missiles[0]].start(msg.x, msg.y, msg.z, time)
                #пишу пбу
                Simulated._sendMessage(MissileStarted(msg.priority, msg.time, self.ID, msg.sender_ID, self.missiles[free_missiles[0]].ID))
                # обновляем во

                #удаляем зур
                free_missiles.pop(0)

        #удаляем мёртвые зур
        for ind in killed_missiles:
            self.missiles.pop(ind)









