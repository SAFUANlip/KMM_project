from src.classes.Simulated import Simulated
from src.classes.ModelDispatcher import ModelDispatcher
from src.messages.BaseMessage import BaseMessage
from numpy.random import randint

############################# Messages ##########################

class RequestMessage(BaseMessage):
###
### Стрелок задаёт загадку всем бегунам
###
### msg type = 1, priority = 10 
###
    def __init__(self, time: int, sender_ID: int, request: str) -> None:
        super(RequestMessage, self).__init__(1, 10, time, sender_ID, -1)
        self.request = request


class AnswerMessage(BaseMessage):
###
### Бегун отвечает на загадку
###
### msg type = 2, priority = 10 
###
    def __init__(self, time: int, sender_ID: int, receiver_ID: int, answer: str) -> None:
        super(AnswerMessage, self).__init__(2, 10, time, sender_ID, receiver_ID)
        self.answer = answer


class ShotMessage(BaseMessage):
###
### Стрелок стреляет
###
### msg type = 4, priority = 1 
###
    def __init__(self, time: int, sender_ID: int, receiver_ID: int) -> None:
        super(ShotMessage, self).__init__(4, 1, time, sender_ID, receiver_ID)


class HitMessage(BaseMessage):
###
### Бегун кричит, что попали
###
### msg type = 5, priority = 10 
###
    def __init__(self, time: int, sender_ID: int, receiver_ID: int) -> None:
        super(HitMessage, self).__init__(5, 1, time, sender_ID, receiver_ID)

        
#################################################################

class Runner(Simulated):
###
### Бегун, когда приходит сообщение о загадке - отвечает. Когда приходит сообщение о стрельбе - проверяет, попали ли в него
###
    __name: str
    __answer: str

    def __init__(self, dispatcher: ModelDispatcher, ID: int, name: str, answer: str) -> None:
        super(Runner, self).__init__(dispatcher, ID)
        self.__name = name
        self.__answer = answer

    def runSimulationStep(self, time):
        # Получаем сообщения, которые были отправлены этому объекту или всем объектам на предыдущей итерации моделирования
        messages: List[BaseMessage] = self._checkAvailableMessages()
        # Можно отсортировать по приоритету)
        messages.sort(key=lambda x: x.priority, reverse=True)
        for msg in messages:
            if msg.type == 1:
                print(f"time = {time} ### {self.__name} услышал загадку и отвечает: {self.__answer}")
                # отправляем ответное сообщение
                self._sendMessage(AnswerMessage(time, self._ID, msg.sender_ID, self.__answer))
            elif msg.type == 4:
                if randint(100) % 3 == 0:
                    print(f"time = {time} ### {self.__name}: В меня попали((")
                    # отправляем ответное сообщение
                    self._sendMessage(HitMessage(time, self._ID, msg.sender_ID))
                else:
                    print(f"time = {time} ### {self.__name}: Мимо))")




class Shooter(Simulated):
###
### Стрелок, задаёт загадку и ждёт ответ на неё, если какой-то бегун ответил неправильно, то стреляет в него
###
    __is_waiting: bool

    def __init__(self, dispatcher: ModelDispatcher, ID: int) -> None:
        super(Shooter, self).__init__(dispatcher, ID)
        self.__is_waiting = False

    def runSimulationStep(self, time):
        is_shooting: bool = False 
        
        messages: List[BaseMessage] = self._checkAvailableMessages()
        messages.sort(key=lambda x: x.priority, reverse=True)
        for msg in messages:
            if msg.type == 2:
                answer = msg.answer
                self.__is_waiting = False
                if answer == "Лампочка":
                    print(f"time = {time} ### Стрелок услышал правильный ответ")
                else:
                    print(f"time = {time} ### Стелок не услышал правильный ответ и будет стрелять")
                    # отправляем ответное сообщение
                    self._sendMessage(ShotMessage(time, self._ID, msg.sender_ID))
                    is_shooting = True
            elif msg.type == 5:
                print(f"time = {time} ### Стерлок услышал, что попал в предыдущий момент времени")
        if time == 0:
            print(f"time = {time} ### Стрелок будет задавать загадку и стрелять")
        if not is_shooting and not self.__is_waiting:
            print(f"time = {time} ### Стрелок задаёт загадку: Висит груша, нельзя скушать")
            # Делаем рассылку всем объектам
            self._sendMessage(RequestMessage(time, self._ID, "Висит груша, нельзя скушать"))
            self.__is_waiting = True



if __name__ == '__main__':
    dispatcher: ModelDispatcher = ModelDispatcher()
    dispatcher.setSimulatingRate(5)
    dispatcher.setSimulationTime(1.6)
    dispatcher.configurate([Runner(dispatcher, 11, "Петя", "Лампочка"),
                            Runner(dispatcher, 12, "Вася", "Елка"),
                            Shooter(dispatcher, 10)])
    dispatcher.run()