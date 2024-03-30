from src.BaseMessage import BaseMessage

#ответное сообщение для пбу
class MissileStarted(BaseMessage):

    def __init__(self, time: int, sender_ID: int, receiver_ID: int, id_missile: int, order: int) -> None:
        super(MissileStarted, self).__init__(6001, 0, time, sender_ID, receiver_ID)
        self.id_missile = id_missile
        self.order = order

class NoMissiles(BaseMessage):

    def __init__(self, time: int, sender_ID: int, receiver_ID: int, order: int) -> None:
        super(NoMissiles, self).__init__(6002, 0, time, sender_ID, receiver_ID)
        self.order = order