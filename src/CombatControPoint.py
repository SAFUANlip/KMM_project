from src.BaseMessage import BaseMessage
from src.Simulated import Simulated, ModelDispatcher


class CombatControl2RadarMsg(BaseMessage):
    def __init__(self, time: int, sender_ID: int, request: str) -> None:
        super(CombatControl2RadarMsg, self).__init__(55, 10, time, sender_ID= sender_ID, receiver_ID= -1)


class CombatControl2ПУMsg(BaseMessage):
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int) -> None:
        self.type = type
        self.priority = priority
        self.time = time
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID
class CombatControlPoint(Simulated):
    def __init__(self, dispatcher: ModelDispatcher, ID: int):
        self.__dispatcher = dispatcher
        self._ID = ID
        self.target_list = []
        self.rocket_list = []

    def runSimulationStep(self, dispatcher: ModelDispatcher, ID: int):
        self.__dispatcher = dispatcher
        self._ID = ID

    def getAirObjects(self):
        """
        получить объекты, которые видит МФР в виде
        [[x,y,id, type], [x,y,id, type]  .... ]
        type 0 если это цель, 1 - если ракета

        id - уникальный идентификатор объекта
        отсортировать на списки id:
            ракет
            старых целей (к которым ракеты вылетели)
            новых целей (которые только увидели)
        :return: списки id
        """
        air_objects = self._checkAvailableMessagesByType(77)

        old_targets = []
        new_targets = []
        rockets = []

        for air_object in air_objects:
            if air_object[3] == 0:
                target_id = air_object[2]
                if target_id not in self.target_list:
                    new_targets.append(target_id)
                else:
                    old_targets.append(target_id)
            else:
                rockets.append(air_object[2])
        return rockets, old_targets, new_targets


    def send2 ПУ NewTargets(self, new_targets):
        pass

    def send2RadarOldTargets(self, old_targets):
        msg = CombatControl2RadarMsg()







