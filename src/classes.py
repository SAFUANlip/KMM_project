import numpy as np


class ZUR(object):
    def __init__(self, x, y, z, speed, expl_radius, x_target, y_target, z_target):
        self.x = x,
        self.y = y,
        self.z = z,
        self.speed = speed,
        self.expl_radius = expl_radius,
        self.x_target = x_target,
        self.y_target = y_target,
        self.z_target = z_target,

    def update_target(self, x_target, y_target, z_target):
        self.x_target = x_target,
        self.y_target = y_target,
        self.z_target = z_target,

    def is_hit(self):
        pass
    

