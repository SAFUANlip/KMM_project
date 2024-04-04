from src.modules_classes.AeroEnv import AeroEnv, Airplane
from src.modules_classes.CombatControPoint import CombatControlPoint
from src.modules_classes.Radar import RadarRound
from src.modules_classes.StartingDevice import StartingDevice
from src.modules_classes.ModelDispatcher import ModelDispatcher
from random import randint
import numpy as np

if __name__ == '__main__':
    dispatcher = ModelDispatcher()
    dispatcher.setSimulatingRate(1)
    dispatcher.setSimulationTime(25)

    n = 1

    targets = [Airplane(dispatcher=dispatcher, ID=1, pos=np.array([10000, 10000, 10000]), rad=5, vel=np.array([100, 100, 100]),
                        t_start=0, t_end=100),
               Airplane(dispatcher=dispatcher, ID=2, pos=np.array([-10000, 10000, 10000]), rad=5,
                        vel=np.array([100, 100, 100]),
                        t_start=0, t_end=100)
               ]
    env = AeroEnv(dispatcher, len(targets))
    for el in targets:
        env.addEntity(el)

    radar = RadarRound(dispatcher, 1, 3000, env, (10, 10, 0), 0, 0, 500000, 120, 90)
    start_devices = [StartingDevice(dispatcher, 2000, np.array([0, 0, 0]), env)]
    starting_devices_coords = {}
    for sd in start_devices:
        starting_devices_coords[sd._ID] = sd.pos
    combat = CombatControlPoint(dispatcher, 3000, starting_devices_coords)

    dispatcher.configurate([env, radar, combat, *start_devices])
    dispatcher.run()

    # rate, messages_classes = dispatcher.getMessageHistory()
    # for i in range(len(messages_classes)):
    #     print(f"time: {i/rate}")
    #
    #     for message in messages_classes[i]:
    #         print(f"time: {i/rate} ", vars(message))
