import numpy as np

from src.classes.ModelDispatcher import ModelDispatcher, Simulated


class Movable(Simulated):
    def __init__(self, dispathcer: ModelDispatcher, ID: int,
                 pos: np.array([float, float, float]),
                 vel: np.array([float, float, float])) -> None:
        super().__init__(dispathcer, ID, pos)
        self.vel = vel