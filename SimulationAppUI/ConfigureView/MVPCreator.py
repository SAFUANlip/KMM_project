from SimulationAppUI.ConfigureView.Models import *
from SimulationAppUI.ConfigureView.GraphicComponents import *
from SimulationAppUI.ConfigureView.GraphicComponentPresenter import *


class MVPCreator:
    def __init__(self):
        self.map = {
            1 : [ControlPointSource, SimpleGraphicComponent, GraphicComponentPresenter],
            2 : [RadarSource, RadarGraphicComponent, GraphicRadarPresenter],
            3 : [StartDeviceSource, SimpleGraphicComponent, GraphicComponentPresenter],
            4 : [AeroTargetSource, GraphicAeroTargetComponent, GraphicAeroTargetPresenter] }

    def create(self, model_type, id, x, y, translator, pixmap, start_drag_distance):
        m_f, v_f, p_f = self.map[model_type // 1000]
        m = m_f(id, model_type, x, y)
        v = v_f(pixmap, start_drag_distance, translator.grid)
        p = p_f(m, v, translator)
        return m, v, p

    def createByModel(self, model, translator, pixmap, start_drag_distance):
        _, v_f, p_f = self.map[model.model_type // 1000]
        v = v_f(pixmap, start_drag_distance, translator.grid)
        p = p_f(model, v, translator)
        return v, p
