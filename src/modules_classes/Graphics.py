from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from src.modules_classes.Simulated import Simulated
from src.modules_classes.GuidedMissile import GuidedMissile
import matplotlib.pyplot as plt
from src.modules_classes.AeroEnv import AeroEnv, Airplane, Helicopter
from config.constants import MSG_RADAR2DRAWER_type, MSG_CCP2DRAWER_type, MISSILE_TYPE_DRAWER

import time as time_python

class Graphics(Simulated):
    def __init__(self, dispatcher, ID: int, aero_env: AeroEnv) -> None:
        super().__init__(dispatcher=dispatcher, ID=ID, pos=None)
        self.aero_env = aero_env

    def runSimulationStep(self, time: float) -> None:
        fig, ax = plt.subplots(1, 3, figsize=(20, 7))

        plt.ion()

        for el in ax:
            el.set_xlim(-50000, 50000)
            el.set_ylim(-50000, 50000)
            el.xaxis.set_major_locator(MultipleLocator(10000))
            el.yaxis.set_major_locator(MultipleLocator(10000))

            # Change minor ticks to show every 5. (20/4 = 5)
            # el.xaxis.set_minor_locator(AutoMinorLocator(4))
            # el.yaxis.set_minor_locator(AutoMinorLocator(4))
            el.grid()

        MFR_list = self._checkAvailableMessagesByType(MSG_RADAR2DRAWER_type)  #.pos_objects\

        print(len(MFR_list), "Я ГРАФИКА")
        if len(MFR_list) > 0:
            MFR_msg = MFR_list[0].pos_objects
            for i in range(len(MFR_msg)):
                ax[0].scatter(MFR_msg[i][0], MFR_msg[i][1], marker='o', color='b')

        CCP_list = self._checkAvailableMessagesByType(MSG_CCP2DRAWER_type)  #.pos_objects
        if len(CCP_list) > 0:
            CCP_msg = CCP_list[0].pos_objects
            # 0 - зур, 1 - цель
            line1, line2 = None, None
            for i in range(len(CCP_msg)):
                print(CCP_msg[i])
                if CCP_msg[i][0] == MISSILE_TYPE_DRAWER:
                    line1 = ax[1].scatter(CCP_msg[i][1][0], CCP_msg[i][1][1], marker='^', color='g', label="GuidedMissile")
                else:
                    line2 = ax[1].scatter(CCP_msg[i][1][0], CCP_msg[i][1][1], marker='o', color='r', label="Target")


        aims = self.aero_env.getEntities()
        if len(aims) > 0:
            line1, line2, line3 = None, None, None
            for aim in aims:
                if isinstance(aim, Airplane):
                    line1 = ax[2].scatter(aim.pos[0], aim.pos[1], marker='o', color='r', label='Plane')

                elif isinstance(aim, Helicopter):
                    line2 = ax[2].scatter(aim.pos[0], aim.pos[1], marker='*', color='m', label='Helicopter')

                elif isinstance(aim, GuidedMissile):
                    line3 = ax[2].scatter(aim.pos[0], aim.pos[1], marker='^', color='g', label='GuidedMissile')

            ax[2].legend((line1, line2, line3), ['Plane', 'Helicopter', 'GuidedMissile'])

        fig.canvas.draw()
        fig.canvas.flush_events()

        time_python.sleep(0.5)
        plt.close(fig)