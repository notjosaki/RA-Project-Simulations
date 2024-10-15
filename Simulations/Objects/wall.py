import numpy as np

class Wall:
    def __init__(self, position, width, height):
        self.position = np.array(position)
        self.width = width
        self.height = height

    def check_collision(self, sphere):
        # Comprobamos la colisión con el muro
        if (sphere.position[0] + sphere.radius > self.position[0] and
                sphere.position[0] - sphere.radius < self.position[0] + self.width and
                sphere.position[1] - sphere.radius < self.position[1] + self.height and
                sphere.position[1] + sphere.radius > self.position[1]):
            return True
        return False

    def resolve_collision(self, sphere):
        # Rebote de la esfera con el muro
        if sphere.position[0] + sphere.radius > self.position[0] and sphere.velocity[0] > 0:
            sphere.position[0] = self.position[0] - sphere.radius
            sphere.velocity[0] = -sphere.velocity[0]
        elif sphere.position[0] - sphere.radius < self.position[0] + self.width and sphere.velocity[0] < 0:
            sphere.position[0] = self.position[0] + self.width + sphere.radius
            sphere.velocity[0] = -sphere.velocity[0]
