class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def sum(self, vec_b):
        return Vector(self.x + vec_b.x, self.y + vec_b.y, self.z + vec_b.z)

    def sub(self, vec_b):
        return Vector(self.x - vec_b.x, self.y - vec_b.y, self.z + vec_b.z)

    def __str__(self):
        return f"Vector({round(self.x, 3)}, {round(self.y, 3)}, {round(self.z, 3)})"