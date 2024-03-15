from BaseMessage import BaseMessage

class Radar2CombatControlMsg(BaseMessage):
    def __init__(self, type: int, priority: int, time: int, sender_ID: int, receiver_ID: int, visible_objects: list):
        '''
        :param visible_objects: список видимых объектов из списков типа
                                [положение объекта, направление скорости объекта, модуль скорости объекта]
        '''
        super().__init__(type, priority, time, sender_ID, receiver_ID)
        self.visible_objects = visible_objects