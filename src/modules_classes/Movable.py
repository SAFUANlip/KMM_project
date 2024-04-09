import numpy as np

from src.modules_classes.ModelDispatcher import ModelDispatcher, Simulated


class Movable(Simulated):
    def __init__(self, dispathcer: ModelDispatcher, ID: int,
                 pos: np.array([float, float, float]),
                 vel: np.array([float, float, float]),
                 size: float) -> None:
        super().__init__(dispathcer, ID, pos)
        self.vel = vel
        self.size = size