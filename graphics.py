from src.classes.Simulated import Simulated
from src.classes.GuidedMissile import GuidedMissile
import matplotlib.pyplot as plt
from src.classes.AeroEnv import AeroEnv, Airplane, Helicopter
from config.constants import MSG_RADAR2DRAWER_type, MSG_CCP2DRAWER_type

class Graphics(Simulated):
    def __init__(self, dispatcher, ID: int, aero_env: AeroEnv) -> None:
        super().__init__(__dispatcher=dispatcher, _ID=ID)
        self.aeroenv = AeroEnv

    def runSimulationStep(self, time: float) -> None:
        fig, ax = plt.subplots(1, 3, figsize=(10, 10))

        MFR_list = self._checkAvailableMessagesByType(MSG_RADAR2DRAWER_type).coordinates
        for i in MFR_list:
            ax[0].scatter(MFR_list[i][0], MFR_list[i][1], marker='o', color = 'b')

        PBU_list = self._checkAvailableMessagesByType(MSG_CCP2DRAWER_type).coordinates
        # 0 - зур, 1 - цель
        for i in PBU_list:
            if(PBU_list[i][0] == 0):
                line1 = ax[1].scatter(PBU_list[i][1][0], PBU_list[i][1][1], marker='^', color = 'g')
            else:
                line2 = ax[1].scatter(PBU_list[i][1][0], PBU_list[i][1][1], marker='o', color='r')

        ax[1].legend((line1, line2), ['зур', 'цель'])

        aims = self.aeroenv.getEntities()
        for aim in aims:
            if isinstance(aim, Airplane):
                line1 = ax[2].scatter(aim.pos[0], aim.pos[1], marker='o', color='r', label = 'самолет')

            elif isinstance(aim, Helicopter):
                line2 = ax[2].scatter(aim.pos[0], aim.pos[1], marker='*', color='m', label = 'вертолет')

            elif isinstance(aim, GuidedMissile):
                line3 = ax[2].scatter(aim.pos[0], aim.pos[1], marker='^', color='g', label = 'зур')

        ax[2].legend((line1, line2, line3), ['самолет', 'вертолет', 'зур'])

        plt.show()
