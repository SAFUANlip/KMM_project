from config.constants import MISSILE_INIT_SPEED
from src.messages.Messages import CombatControl2StartingDeviceMsg
from src.classes.Simulated import Simulated, ModelDispatcher


class CombatControlPoint(Simulated):
    def __init__(self, dispatcher: ModelDispatcher, ID: int):
        self.__dispatcher = dispatcher
        self._ID = ID
        self.all_id = {}
        self.target_list = []
        self.missile_list = []
        self.StartingDevices_coords = {}


    def runSimulationStep(self, time: int) -> None:
        """
        """
        msgFromRadar = self._checkAvailableMessagesByType(2001)

        if len(self.target_list) == 0: # начало программы, когда на поле только цели
            for visible_objects in msgFromRadar:
                coord = visible_objects #FIXME извлвечь координаты
                speed = visible_objects #FIXME извлечь искорость

                self.target_list.append([coord, speed]) # положить в память новые цели
                msg2StartingDevice = CombatControl2StartingDeviceMsg(3001, len(self.target_list) - 1, time, self._ID, self.all_id["ПУ"], coord)
                self._sendMessage(msg2StartingDevice) # сказала ПУ, что нужно запустить ЗУР по координатам coord
        else:
            # получить id  ЗУР, которые ПУ отправила
            msgsFromStartingDevice = self._checkAvailableMessagesByType(6001)
            if not isinstance(msgsFromStartingDevice, list):
                msgsFromStartingDevice = [msgsFromStartingDevice]

            # дальше надо соотнести id ЗУР, координаты ЗУР и координаты их Целей
            for msgFromStartingDevice in msgsFromStartingDevice:
                missile_id = msgFromStartingDevice.missile_id
                StartingDevice_id = msgFromStartingDevice.sender_ID
                missile_coord = self.StartingDevices_coords[StartingDevice_id]

                target_num_list = msgFromStartingDevice.priority

                target_coord = self.target_list[target_num_list]
                self.missile_list.append([missile_coord, target_coord, missile_id, MISSILE_INIT_SPEED]) # коорд зур, коорд ее цели, id зур, скорость зур
                self.target_list.append(target_coord)  #добавили цели, которые получили на предыдущем шаге


            # смотрю на координаты объектов, которые видит МФР и выбираю, кто из них новые цели, кто старые цели, кто старые зур
            for visible_objects in msgFromRadar:
                coord = visible_objects  # FIXME извлвечь координаты
                speed = visible_objects  # FIXME извлечь искорость




















