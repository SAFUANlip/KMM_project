from src.modules_classes.AeroEnv import AeroEnv, Airplane
from src.modules_classes.Radar import RadarRound
from src.modules_classes.ModelDispatcher import ModelDispatcher
from random import randint
import numpy as np

if __name__ == '__main__':
    dispatcher = ModelDispatcher()
    dispatcher.setSimulatingRate(10)
    dispatcher.setSimulationTime(1)

    n = 3
    targets = [Airplane(dispatcher=dispatcher, ID=1000+i,
                       pos=np.array([randint(-20000, 20000), randint(-20000, 20000), randint(400, 7000)]), 
                       vel=np.array([randint(-2, 2)]*3), rad=5) for i in range(n)]
    env = AeroEnv(dispatcher, len(targets))
    for el in targets:
        env.addEntity(el)
    radar = RadarRound(dispatcher, 1, 3000, env, (0, 0, 0), 0, 0, 50000, 120 * np.pi / 180, 60 * np.pi / 180)
    dispatcher.configurate([env, radar])
    dispatcher.run()


    rate, messages = dispatcher.getMessageHistory()
    for i in range(len(messages)):
        print(f"time: {i/rate}")
        for message in messages[i]:
            print(f"time: {i/rate} ", vars(message))

