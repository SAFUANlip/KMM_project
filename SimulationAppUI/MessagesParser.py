import numpy as np

from src.modules_classes.AeroEnv import AeroEnv, Airplane, Helicopter
from src.modules_classes.Radar import RadarRound
from src.modules_classes.StartingDevice import StartingDevice
from src.modules_classes.CombatControPoint import CombatControlPoint

from config.constants import MSG_RADAR2DRAWER_type, MSG_CCP2DRAWER_type

def parse_messages(all_messages):
    objs = {"radars": [1, 2, 3], "controls": [1, 2], "vo": [0], }
    trajs = {
        "radars": {1:
                       {259: [np.array([10, 10]), np.array([20, 20]), np.array([30, 30])],
                        260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
                   2:
                       {259: [np.array([10, 10]), np.array([20, 20]), np.array([400, 50])],
                        260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
                   3:
                       {259: [np.array([10, 10]), np.array([20, 20]), np.array([400, 50])],
                        260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]}
                   },
        "controls": {1:
                          {259: [np.array([10, 10]), np.array([20, 20]), np.array([30, 30])],
                           260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]},
                      2:
                          {259: [np.array([10, 10]), np.array([20, 20]), np.array([400, 50])],
                           260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]}
                      },
        "vo": {
                259: [np.array([20000, 20000]), np.array([20000, 6000]), np.array([30, 30])],
                260: [np.array([100, 200]), np.array([200, 200]), np.array([300, 300])]
               },
    }
    return objs, trajs
