import numpy as np

from src.classes.ModelDispatcher import ModelDispatcher, Simulated


class Movable(Simulated):
    def __init__(self, dispathcer: ModelDispatcher, ID: int,
                 pos: np.array([int, int, int]),
                 vel: np.array([int, int, int])) -> None:
        super().__init__(dispathcer, ID, pos)
        self.vel = vel