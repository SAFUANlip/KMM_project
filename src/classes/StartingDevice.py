import typing
from typing import List, Tuple
from config.constants import NUMBER_OF_MISSILES
from src.classes.AeroEnv import AeroEnv
from src.classes.GuidedMissile import GuidedMissile
from src.classes.ModelDispatcher import ModelDispatcher
from src.classes.Simulated import Simulated
from src.messages.Messages import NoMissiles, MissileStarted
from src.utils.logger import logger

# класс ПУ
class StartingDevice(Simulated):
    missiles: list # список имеющихся зур
    # координаты пу
    x: int
    y: int
    z: int

    def __init__(self, dispatcher: ModelDispatcher, ID: int, x: int, y: int, z: int, aero_env: AeroEnv) -> None:
        super().__init__(dispatcher, ID)
        self.x = x
        self.y = y
        self.z = z
        self.aeroenv = aero_env
        self.missiles = [GuidedMissile( dispatcher, self._ID * 1000 + i, self.x, self.y, self.z) for i in range(NUMBER_OF_MISSILES)]

    # проверяем статусы зур, заполняем список убивших цель и неактивных
    def checkMissiles(self) -> Tuple[List[int], List[int]]:
        free_missiles = []
        killed_missiles = []

        for i in range(len(self.missiles)):
            status = self.missiles[i].getStatus()
            if status == 0:
                free_missiles.append(self.missiles[i])
            elif status == 2:
                killed_missiles.append(self.missiles[i])

        return free_missiles, killed_missiles


    def runSimulationStep(self, time: float) -> None:
        # узнаём статус всех зур
        free_missiles, killed_missiles = self.checkMissiles()
        # проверяем почту на наличие сообщений от пбу и запускаем ракеты
        new_messages = self._checkAvailableMessagesByType(msg_type = 3001)
        for msg in new_messages:
            # проверка наличия свободных зур
            logger.starting_device(f"ПУ с id {self._ID} получило сообщение от ПБУ с id {msg.sender_ID}")
            if len(free_missiles) == 0:
                # если нет - сигналим
                self._sendMessage(NoMissiles(time, self._ID, msg.sender_ID, msg.order)) # если нет - сигналим
                logger.starting_device(f"ПУ с id {self._ID} отправила ПБУ сообщение об отсутствии ЗУР")
            else:
                logger.starting_device(f"ПУ с id {self._ID} получила координаты {msg.coord} от ПБУ")
                # если есть - запускаем
                free_missiles[0].launch(*msg.coord, time)
                #пишу пбу
                logger.starting_device(f"ПУ с id {self._ID} запустила ЗУР с id {free_missiles[0]._ID}")
                self._sendMessage(MissileStarted(time, self._ID, msg.sender_ID, free_missiles[0]._ID, msg.order))
                logger.starting_device(f"ПУ с id {self._ID} отправила сообщение ПБУ о запуске ЗУР")
                # обновляем во
                self.aeroenv.addEntity(free_missiles[0])
                #удаляем зур
                free_missiles.pop(0)

        #удаляем мёртвые зур
        for ind in killed_missiles:
            self.missiles.pop(ind)