from simulation_process.constants import DRAWER_ID
from simulation_process.modules_classes.AeroEnv import AeroEnv, Airplane
from simulation_process.modules_classes.CombatControPoint import CombatControlPoint
from simulation_process.modules_classes.Radar import RadarRound, RadarSector
from simulation_process.modules_classes.StartingDevice import StartingDevice
from simulation_process.modules_classes.ModelDispatcher import ModelDispatcher
from simulation_process.modules_classes.Graphics import Graphics
import numpy as np

if __name__ == '__main__':
    dispatcher = ModelDispatcher()
    dispatcher.setSimulatingRate(1)
    dispatcher.setSimulationTime(70)

    n = 1
    targets = [
               Airplane(dispatcher=dispatcher, ID=3, vel=np.array([100,100,100]), size=5,
                        trajectory_planned=[np.array([0, 10000, 10000]),
                                            np.array([10000, 0, 10000]),
                                            np.array([10000, 10000, 11000])],
                        start_time=0, end_time=100),
               Airplane(dispatcher=dispatcher, ID=4, vel = np.array([100,100,100]),
                        trajectory_planned=[np.array([-10000, -10000, 10000])], size=5,
                        start_time=10, end_time=120),
               Airplane(
                   dispatcher=dispatcher, ID=5, vel=np.array([100,100,100]),
                   trajectory_planned=[np.array([-1000, -1000, 10000]),
                                       np.array([-1100, -1000, 10000]),
                                       np.array([-1200, -1100, 10000]),
                                       np.array([-1300, -1200, 10000])],
                   size=5,
                   start_time=0,
                   end_time=140),
                Airplane(
                   dispatcher=dispatcher, ID=5, vel=np.array([100,100,100]),
                   trajectory_planned=[np.array([-20000, 10000, 10000]),
                                       np.array([-22000, 15000, 7000]),
                                       np.array([-24000, 20000, 5000]),
                                       np.array([-24000, -25000, 5000])],
                   size=5,
                   start_time=0,
                   end_time=140
               )
               ]

    env = AeroEnv(dispatcher, len(targets), targets=targets)

    radar = RadarRound(dispatcher, 1, 3000, env, (10, 10, 0), 0, 0, 50000, 360, 180)
    radar2 = RadarSector(dispatcher, 2, 3000, env, (-100, -100, 0), 0, 0, 50000, 180, 180, 90, 90)

    start_devices = [StartingDevice(dispatcher, 2000, np.array([0, 0, 0]), env)]
    starting_devices_coords = {}
    for sd in start_devices:
        starting_devices_coords[sd._ID] = sd.pos
    combat = CombatControlPoint(dispatcher, 3000, starting_devices_coords)

    graphics = Graphics(dispatcher=dispatcher, ID=DRAWER_ID, aero_env=env)

    dispatcher.configurate([env, radar, radar2, combat, *start_devices, graphics])
    dispatcher.run()

    # rate, messages_classes = dispatcher.getMessageHistory()
    # for i in range(len(messages_classes)):
    #     print(f"time: {i/rate}")
    #
    #     for message in messages_classes[i]:
    #         print(f"time: {i/rate} ", vars(message))
