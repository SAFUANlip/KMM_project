import numpy as np

from src.modules_classes.ModelDispatcher import ModelDispatcher, Simulated


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

        angle_between((1, 0, 0), (0, 1, 0))
        1.5707963267948966

        angle_between((1, 0, 0), (1, 0, 0))
        0.0

        angle_between((1, 0, 0), (-1, 0, 0))
        3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def dist(pos1: np.array, pos2: np.array) -> float:
    return np.linalg.norm(pos1 - pos2)


class Movable(Simulated):
    def __init__(self, dispathcer: ModelDispatcher, ID: int,
                 pos: np.array([float, float, float]),
                 vel: np.array([float, float, float]),
                 size: float,
                 speed: float) -> None:
        super().__init__(dispathcer, ID, pos)
        self.vel = vel
        self.size = size
        self.speed = speed
